import airsim
# connect to the AirSim simulator
client = airsim.MultirotorClient()
client.simLoadLevel('Qualifier_Tier_2')

client.confirmConnection()
# get control
client.enableApiControl(True)
# unlock
client.armDisarm(True)

# Async methods returns Future. Call join() to wait for task to complete.
client.takeoffAsync().join()

client.moveToZAsync(-30, 10).join()               # 上升到3m高度
try:
    client.moveToPositionAsync(15, 15, -15, 5).join()
except Exception as e:
    print(f"Movement failed: {str(e)}")


client.landAsync().join()       # land
client.armDisarm(False)         # lock
client.enableApiControl(False)  # release control