import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from matching.models import MatchingQuestion
from users.models import User
from users.serializers import ProfileCompletionSerializer
from .serializers import MatchingQuestionSerializer
import pandas as pd
import pickle
import pulp


# Create your views here.
class QuestionListView(APIView):
    def get(self, request):
        questions = MatchingQuestion.objects.all()
        serializer = MatchingQuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MatchingView(APIView):
    def post(self, request):
        user_id = request.user.id
        users = User.objects.all()
        complete_users = [
            user for user in users
            if ProfileCompletionSerializer(user).data['is_profile_complete']
        ]
        user = User.objects.get(id=user_id)
        user.preferred_distance = request.data["responses"].get("Preferred Distance", None)
        user.save()

        # Convert queryset to list of dictionaries
        data = [
            {
                'ID': user.id,
                'Name': user.first_name,
                'Family Name': user.last_name,
                'Age': user.age,
                'Gender': "Male" if user.gender == "0" else "Female" if user.gender == "1" else "",
                'Province': user.province,
                'City': user.city,
                'Level of experties': user.level_of_expertise,
                'Personality (Social)': user.personality_social,
                'Personality (Detail)': user.personality_detail,
                'Decision Making': user.decision_making,
                'Planning Style': user.planning_style,
                'Instrument': user.preferred_instrument,
                "Prefered distance": user.preferred_distance if user.preferred_distance is not None else "20000",
                'Genres': user.favorite_genre,
                'Available time for train': user.available_time,
                'Own song': user.own_song,
                'Academic Knowledge': user.academic_knowledge,
                'Clothing style': user.preferred_clothing,
                'Combined Personality': f"{user.personality_social}{user.personality_detail}{user.decision_making}{user.planning_style}"
            }
            for user in complete_users
        ]
        # Create DataFrame
        dataset = pd.DataFrame(data)

        if request.data["responses"]["Academic Knowledge"] != "Never mind":
            dataset = dataset[
                (dataset["Academic Knowledge"] == request.data["responses"]["Academic Knowledge"]) |
                (dataset["ID"] == user_id)
                ]

        if request.data["responses"]["Gender"] != "Never mind":
            dataset = dataset[
                (dataset["Gender"] == request.data["responses"]["Gender"]) |
                (dataset["ID"] == user_id)
                ]

        if request.data["responses"]["Own Song"] != "Never mind":
            dataset = dataset[
                (dataset["Own song"] == request.data["responses"]["Own Song"]) |
                (dataset["ID"] == user_id)
                ]

        if request.data["responses"]["Clothing Style"] != "Never mind":
            dataset = dataset[
                (dataset["Clothing style"] == request.data["responses"]["Clothing Style"]) |
                (dataset["ID"] == user_id)
                ]

        dataset = dataset[
            (dataset["Instrument"] == request.data["responses"]["Instrument"]) |
            (dataset["ID"] == user_id)
            ]
        copy_dataset = dataset.copy()

        ids = dataset['ID'].unique()  # Get unique IDs
        n = len(ids)

        if n == 1:
            request.user.matched_users.set([])
            return Response("Empty", status=status.HTTP_200_OK)


        with open("matching/optimization/MBTI_Compatibility.pkl", "rb") as f:
            MBTI_Compatibility_score = pickle.load(f)

        with open("matching/optimization/Genres_Compatibility.pkl", "rb") as f:
            Genres_Compatibility_score = pickle.load(f)

        with open("matching/optimization/Level_Compatibility.pkl", "rb") as f:
            Level_Compatibility_score = pickle.load(f)

        with open("matching/optimization/Ahours_Compatibility.pkl", "rb") as f:
            Ahours_compatibility = pickle.load(f)

        # Load Distance Cities Matrix
        with open("matching/optimization/DistCities.pkl", "rb") as f:
            DistCities = pickle.load(f)

        ages = dataset.set_index('ID')['Age']  # Create a mapping of ID to age

        DiffAge = np.zeros((n, n))

        # Fill the matrix with absolute differences in age
        for i in range(n):
            for j in range(n):
                DiffAge[i, j] = abs(ages[ids[i]] - ages[ids[j]])

        # Convert to a DataFrame for better readability
        DiffAge_df = pd.DataFrame(DiffAge, index=ids, columns=ids)
        n = DiffAge.shape[0]  # Get the size of the matrix
        SDiffAge = np.zeros((n, n))  # Initialize the score matrix
        age_std = dataset["Age"].std()
        age_ave = dataset["Age"].mean()

        # Apply scoring conditions
        for i in range(n):
            for j in range(n):
                if 0 < DiffAge[i, j] <= age_std:
                    SDiffAge[i, j] = 10
                elif age_std < DiffAge[i, j] < 2 * age_std:
                    SDiffAge[i, j] = 5
                else:
                    SDiffAge[i, j] = 1

        # Convert to DataFrame for better readability
        SDiffAge_df = pd.DataFrame(SDiffAge, index=DiffAge_df.index, columns=DiffAge_df.columns)
        # Normalize the SDiffAge matrix
        SDiffAge_norm = (SDiffAge - SDiffAge.min()) / (SDiffAge.max() - SDiffAge.min())

        # Convert to DataFrame for better readability
        SDiffAge_df = pd.DataFrame(SDiffAge, index=DiffAge_df.index, columns=DiffAge_df.columns)
        SDiffAge_norm_df = pd.DataFrame(SDiffAge_norm, index=DiffAge_df.index, columns=DiffAge_df.columns)

        dataset['Combined Personality'] = dataset['Combined Personality'].astype(
            str).str.strip().str.upper()

        MBTI_Compatibility_score.set_index("Personality Types", inplace=True)

        # Ensure index and columns are properly formatted (remove spaces, ensure uppercase)
        MBTI_Compatibility_score.index = MBTI_Compatibility_score.index.astype(str).str.strip().str.upper()
        MBTI_Compatibility_score.columns = MBTI_Compatibility_score.columns.astype(str).str.strip().str.upper()

        # Extract unique IDs and map ID to personality type
        ids = dataset['ID'].unique()
        personalities = dataset.set_index('ID')['Combined Personality']

        # Create an empty matrix for personality compatibility scores
        n = len(ids)
        SPersType = np.zeros((n, n))

        # Fill the matrix with compatibility scores
        for i in range(n):
            for j in range(n):
                pers_i = personalities.get(ids[i], None)  # Get personality type or None
                pers_j = personalities.get(ids[j], None)

                if pers_i in MBTI_Compatibility_score.index and pers_j in MBTI_Compatibility_score.columns:
                    SPersType[i, j] = MBTI_Compatibility_score.at[pers_i, pers_j]
                else:
                    print(f"Skipping ID {ids[i]} ({pers_i}) and {ids[j]} ({pers_j}) - Personality Type Not Found!")

        # Convert to a DataFrame for better readability
        SPersType_df = pd.DataFrame(SPersType, index=ids, columns=ids)
        # Normalize SPersType_df using Min-Max Scaling
        SPersType_norm_df = (SPersType_df - SPersType_df.min().min()) / (
                SPersType_df.max().max() - SPersType_df.min().min())

        # Assuming `dataset` contains the ID and Combined Personality column
        dataset['Genres'] = dataset['Genres'].astype(str).str.strip().str.upper()

        Genres_Compatibility_score.set_index("Genres", inplace=True)

        # Ensure index and columns are properly formatted (remove spaces, ensure uppercase)
        Genres_Compatibility_score.index = Genres_Compatibility_score.index.astype(str).str.strip().str.upper()
        Genres_Compatibility_score.columns = Genres_Compatibility_score.columns.astype(str).str.strip().str.upper()

        # Extract unique IDs and map ID to personality type
        ids = dataset['ID'].unique()
        GENRES = dataset.set_index('ID')['Genres']

        n = len(ids)
        SGenresType = np.zeros((n, n))

        # Fill the matrix with compatibility scores
        for i in range(n):
            for j in range(n):
                genre_i = GENRES.get(ids[i], None)  # Get preferred genre or None
                genre_j = GENRES.get(ids[j], None)

                if genre_i in Genres_Compatibility_score.index and genre_j in Genres_Compatibility_score.columns:
                    score = Genres_Compatibility_score.at[genre_i, genre_j]
                    SGenresType[i, j] = score  # Assign compatibility score
                else:
                    print(f"Skipping ID {ids[i]} ({genre_i}) and {ids[j]} ({genre_j}) - Genre Not Found!")

        # Convert to a DataFrame for better readability
        SGenresType_df = pd.DataFrame(SGenresType, index=ids, columns=ids)
        SGenresType_norm = (SGenresType_df - SGenresType_df.min().min()) / (
                SGenresType_df.max().max() - SGenresType_df.min().min())

        # Convert to a DataFrame
        SGenresType_norm_df = pd.DataFrame(SGenresType_norm, index=SGenresType_df.index, columns=SGenresType_df.columns)

        # Assuming `dataset` contains the ID and Combined Personality column
        dataset['Level of experties'] = dataset['Level of experties'].astype(
            str).str.strip().str.upper()

        Level_Compatibility_score.set_index("Level", inplace=True)

        # Ensure index and columns are properly formatted (remove spaces, ensure uppercase)
        Level_Compatibility_score.index = Level_Compatibility_score.index.astype(str).str.strip().str.upper()
        Level_Compatibility_score.columns = Level_Compatibility_score.columns.astype(str).str.strip().str.upper()

        # Extract unique IDs and map ID to personality type
        ids = dataset['ID'].unique()
        LEVELS = dataset.set_index('ID')['Level of experties']

        n = len(ids)
        SLevelsType = np.zeros((n, n))

        # Fill the matrix with compatibility scores
        for i in range(n):
            for j in range(n):
                AHours_i = LEVELS.get(ids[i], None)  # Get preferred genre or None
                AHours_j = LEVELS.get(ids[j], None)

                if AHours_i in Level_Compatibility_score.index and AHours_j in Level_Compatibility_score.columns:
                    score = Level_Compatibility_score.at[AHours_i, AHours_j]
                    SLevelsType[i, j] = score  # Assign compatibility score

                else:
                    print(f"Skipping ID {ids[i]} ({AHours_i}) and {ids[j]} ({AHours_j}) - Genre Not Found!")

        # Convert to a DataFrame for better readability
        SLevelsType_df = pd.DataFrame(SLevelsType, index=ids, columns=ids)
        SLevelsType_norm = (SLevelsType_df - SLevelsType_df.min().min()) / (
                SLevelsType_df.max().max() - SLevelsType_df.min().min())

        # Convert to a DataFrame
        SLevelsType_norm_df = pd.DataFrame(SLevelsType_norm, index=SLevelsType_df.index, columns=SLevelsType_df.columns)

        # Assuming `dataset` contains the ID and Combined Personality column
        dataset['Available time for train'] = dataset['Available time for train'].astype(
            str).str.strip().str.upper()

        Ahours_compatibility.set_index("Ahours", inplace=True)

        # Ensure index and columns are properly formatted (remove spaces, ensure uppercase)
        Ahours_compatibility.index = Ahours_compatibility.index.astype(str).str.strip().str.upper()
        Ahours_compatibility.columns = Ahours_compatibility.columns.astype(str).str.strip().str.upper()

        # Extract unique IDs and map ID to personality type
        ids = dataset['ID'].unique()
        AHOURS = dataset.set_index('ID')['Available time for train']

        n = len(ids)
        SAhoursType = np.zeros((n, n))

        # Fill the matrix with compatibility scores
        for i in range(n):
            for j in range(n):
                AHours_i = AHOURS.get(ids[i], None)  # Get preferred genre or None
                AHours_j = AHOURS.get(ids[j], None)

                if AHours_i in Ahours_compatibility.index and AHours_j in Ahours_compatibility.columns:
                    score = Ahours_compatibility.at[AHours_i, AHours_j]
                    SAhoursType[i, j] = score  # Assign compatibility score

                else:
                    print(f"Skipping ID {ids[i]} ({AHours_i}) and {ids[j]} ({AHours_j}) - hours Not Found!")

        # Convert to a DataFrame for better readability
        SAhoursType_df = pd.DataFrame(SAhoursType, index=ids, columns=ids)
        # Normalize the SAhoursType_df matrix using Min-Max Scaling
        SAhoursType_norm = (SAhoursType_df - SAhoursType_df.min().min()) / (
                SAhoursType_df.max().max() - SAhoursType_df.min().min())

        # Convert to a DataFrame
        SAhoursType_norm_df = pd.DataFrame(SAhoursType_norm, index=SAhoursType_df.index, columns=SAhoursType_df.columns)

        Scors_norm_df = SAhoursType_norm_df + SLevelsType_norm_df + SGenresType_norm_df + SPersType_norm_df + SDiffAge_norm_df

        # Ensure city names are stripped and in title case (or adjust to match format in DistCities)
        dataset["City"] = dataset["City"].astype(str).str.strip().str.title()
        dataset["City"] = dataset["City"].astype(str).str.strip().str.title()

        DistCities.set_index("Cities", inplace=True)

        # Ensure index and columns are properly formatted (remove spaces, ensure uppercase)
        DistCities.index = DistCities.index.astype(str).str.strip().str.upper()
        DistCities.columns = DistCities.columns.astype(str).str.strip().str.upper()
        DistCities.index = DistCities.index.astype(str).str.strip().str.title()
        DistCities.columns = DistCities.columns.astype(str).str.strip().str.title()

        # Extract IDs and map each ID to its city
        ids = dataset["ID"].unique()
        id_to_city = dataset.set_index("ID")["City"]

        # Initialize symmetrical distance matrix
        num_ids = len(ids)
        Distbetween = np.zeros((num_ids, num_ids))

        # Fill the matrix with distances
        for i in range(num_ids):
            for j in range(i, num_ids):  # Fill upper triangle
                city_i = id_to_city.get(ids[i])
                city_j = id_to_city.get(ids[j])

                # Debug: Print city pairs being matched

                if city_i in DistCities.index and city_j in DistCities.columns:
                    distance = DistCities.at[city_i, city_j]
                else:
                    distance = np.nan  # If city not found, assign NaN

                Distbetween[i, j] = distance
                Distbetween[j, i] = distance  # Maintain symmetry
                print(distance)

        # Convert to DataFrame
        Distbetween_df = pd.DataFrame(Distbetween, index=ids, columns=ids)

        Sij_df = Scors_norm_df  # Compatibility Score Matrix
        Dij_df = Distbetween_df  # Distance Matrix

        A = 10  # Max matches per member

        ids = copy_dataset["ID"].unique()

        copy_dataset.columns = copy_dataset.columns.str.strip()

        # ✅ Define the problem
        prob = pulp.LpProblem("Member_Matching", pulp.LpMaximize)

        # ✅ Define binary decision variables
        X = pulp.LpVariable.dicts("X", [(i, j) for i in ids for j in ids], cat="Binary")

        # ✅ Objective Function: Maximize total score
        prob += pulp.lpSum(X[i, j] * Sij_df.loc[i, j] for i in ids for j in ids)

        # ✅ Constraint 1: Each member can be assigned to at most A members
        for i in ids:
            prob += pulp.lpSum(X[i, j] for j in ids if i != j) <= A

        # ✅ Constraint 2: Symmetric Constraint (X[i,j] == X[j,i])
        for i in ids:
            for j in ids:
                prob += X[i, j] == X[j, i]

        # ✅ Constraint 3: Distance Constraint using 'Prefered distance' from dataset
        # for i in ids:
        #     Di = copy_dataset.loc[copy_dataset["ID"] == i, "Prefered distance"].values[0]
        #     Di = float(Di)
        #     print("inja ", Di)
        #     prob += pulp.lpSum(X[i, j] * Dij_df.loc[i, j] for j in ids if i != j) <= Di
        request_user_id = user_id  # Only enforce for the request user

        # ✅ Get the preferred distance from the request

        # ✅ Check if the user provided a preferred distance before applying the constraint
        if user.preferred_distance is not None:
            print("this is it ", user.preferred_distance)
            Di_values = copy_dataset.loc[copy_dataset["ID"] == user_id, "Prefered distance"].values
            Di = float(Di_values[0]) if len(Di_values) > 0 and pd.notna(Di_values[0]) else None
            print(f"📏 Distance Constraint: Max Distance for User {user_id} is {Di} km")

            Dij_df.fillna(99999, inplace=True)  # Replace NaNs with a large number

            prob += pulp.lpSum(
                X[user_id, j] * Dij_df.loc[user_id, j]
                for j in ids if user_id != j and not pd.isna(Dij_df.loc[user_id, j])
            ) <= Di
        else:
            print(f"🚀 No preferred distance provided by User {user_id}. Skipping distance constraint.")

        # ✅ Constraint 4: No self-matching (X[i,i] = 0)
        for i in ids:
            prob += X[i, i] == 0

        # 🚀 Solve the optimization problem
        prob.solve()

        print("\n✅ Optimization Completed!")
        print("Status:", pulp.LpStatus[prob.status])

        # 🚀 Step 7: Extract and display results
        matches = []
        for i in ids:
            for j in ids:
                if X[i, j].varValue == 1 and i != j:
                    matches.append((i, j, Sij_df.loc[i, j]))

        matches_df = pd.DataFrame(matches, columns=["ID", "ID 2", "Score"])
        print(matches_df)
        matches_df = matches_df[matches_df["ID"] == user_id].sort_values(by="Score", ascending=False)
        matched_ids = matches_df["ID 2"].tolist()
        print(matches_df)
        request.user.matched_users.set(matched_ids)
        if len(matches_df) == 0:
            return Response("Empty", status=status.HTTP_200_OK)
        return Response("Success.", status=status.HTTP_200_OK)
