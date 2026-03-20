from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DETAILS = "mongodb://localhost:27017"

client = None
database = None
sensors_collection = None
DevicePredictions_collection  = None
aiControl_collection = None
 # pondSafeLevels_collection = None 
pond_collection = None
user_collection = None
admin_collection = None
pond_notifications_collection = None


#not used
pond_problem_collection = None 
Pond_Alerts_Collection =None

def init_db():
    global client, database, sensors_collection, DevicePredictions_collection
    global aiControl_collection, pond_problem_collection, pond_collection, user_collection
    global Pond_Alerts_Collection, admin_collection, pond_notifications_collection
    try:
        client = AsyncIOMotorClient(MONGO_DETAILS)
        database = client.fishpond
        sensors_collection = database.get_collection("sensorsdata")
        DevicePredictions_collection = database.get_collection("DevicePrediction")
        aiControl_collection = database.get_collection("AiButton")
        # pondSafeLevels_collection = database.get_collection("pondSafeLevels")
        pond_problem_collection = database.get_collection("PondProblem") 
        pond_collection = database.get_collection("ponds")
        user_collection = database.get_collection("users")
        admin_collection = database.get_collection("admin")
        pond_notifications_collection = database.get_collection("notification")
        print("\n\n✅ MongoDB initialized successfully! \n\n")
        print("Database:", database.name)
        print("Prediction collection:", DevicePredictions_collection.name)
        print("AI Control collection:", aiControl_collection.name)
        # print("Pond Safe Levels collection:", pondSafeLevels_collection.name)
        print("Pond collection:", pond_collection.name)
        print("User collection:", user_collection.name)
        print("Pond Notifications collection:", pond_notifications_collection.name)
    except Exception as e:
        print("❌ Failed to initialize MongoDB:", e)