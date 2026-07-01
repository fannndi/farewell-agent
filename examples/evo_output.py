class Device:
    def __init__(s,n,s2):s.name=n;s.status=s2

class XiaomiMimoRepository:
    def __init__(s,c):s.creds=c
    def get(s):
        if'xiaomi-mimo'not in s.creds:
            raise ValueError('No active credentials for provider: xiaomi-mimo')
        return Device('Mimo','online')

class DeviceService:
    def __init__(s,r):s.repo=r
    def fetch(s):return s.repo.get()

class ConsoleView:
    def show(s,d):print(f"Device: {d.name}, Status: {d.status}")
    def error(s,m):print(f"ERROR: {m}")

class DeviceController:
    def __init__(s,svc,vw):s.svc=svc;s.vw=vw
    def run(s):
        try:
            d=s.svc.fetch()
            s.vw.show(d)
        except ValueError as e:
            s.vw.error(str(e))

if __name__=="__main__":
    creds={'xiaomi-mimo':'active_token'}  # ponytail:config
    DeviceController(DeviceService(XiaomiMimoRepository(creds)),ConsoleView()).run()
    print("FOOTER")