import windows_toasts
from datetime import datetime, timedelta

# windows_toasts.ToastDisplayImage.fromPath()

def send_text_tosat(title:str,text:str):
    toaster = windows_toasts.WindowsToaster(title)
    newToast = windows_toasts.Toast()
    newToast.text_fields = [text]
    toaster.show_toast(newToast) 

def send_toast_with_icon(title:str,text:list,imgPath:str,jumpto:str):
    displayTime = datetime.now() + timedelta(seconds=10)
    toaster = windows_toasts.WindowsToaster(title)
    newToast = windows_toasts.Toast()
    newToast.text_fields = text
    newToast.launch_action = jumpto
    newToast.AddImage(windows_toasts.ToastDisplayImage.fromPath(imgPath))
    toaster.schedule_toast(newToast, displayTime)