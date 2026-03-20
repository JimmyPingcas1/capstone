from .sendDataRouteDEMO import router as send_data_router
from .AiSensorControlRoute import router as aiSensorControlRouter      
 # from .PondSafeLevelsRoute import router as pondSafeLevelsRouter
from .authRoute import router as auth_router    
from .AdminPanelRoute import router as admin_panel_router
from .SensorDataRoute import router as sensor_data_router
# from .notificationRoute import router as notification_router


# List of all routers
routers = [
    send_data_router,
    aiSensorControlRouter,
    # pondSafeLevelsRouter,
    auth_router,
    admin_panel_router,
    sensor_data_router,
    # notification_router
]
