

from fastapi import HTTPException





# Pet Exceptions

class PetError(HTTPException):
    
    pass


class PetNotFoundError(PetError):
    def __init__(self, pet_id=None):
        message = "Pet not found" if pet_id is None else f"Pet with id {pet_id} not found"
        super().__init__(status_code=404, detail=message)


class PetCreationError(PetError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create pet: {error}")


class PetAlreadyAdoptedError(PetError):
    def __init__(self, pet_id=None):
        message = "Pet already adopted" if pet_id is None else f"Pet with id {pet_id} is already adopted"
        super().__init__(status_code=400, detail=message)



# User Exceptions

class UserError(HTTPException):
    
    pass


class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=404, detail=message)


class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New passwords do not match")


class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")



# Authentication Exceptions

class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)



# Adoption Request Exceptions

class AdoptionRequestError(HTTPException):
    
    pass


class AdoptionRequestNotFoundError(AdoptionRequestError):
    def __init__(self, adopt_id=None):
        message = "Adoption request not found" if adopt_id is None else f"Adoption request with id {adopt_id} not found"
        super().__init__(status_code=404, detail=message)


class AdoptionRequestCreationError(AdoptionRequestError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create adoption request: {error}")


class AdoptionRequestAlreadyProcessedError(AdoptionRequestError):
    def __init__(self, adopt_id=None):
        message = "Adoption request already processed" if adopt_id is None else f"Adoption request with id {adopt_id} has already been processed"
        super().__init__(status_code=400, detail=message)


# Rescue Report Exceptions

class RescueReportError(HTTPException):
    
    pass


class RescueReportNotFoundError(RescueReportError):
    def __init__(self, report_id=None):
        message = "Rescue report not found" if report_id is None else f"Rescue report with id {report_id} not found"
        super().__init__(status_code=404, detail=message)


class RescueReportCreationError(RescueReportError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create rescue report: {error}")


class RescueReportAlreadyProcessedError(RescueReportError):
    def __init__(self, report_id=None):
        message = "Rescue report already processed" if report_id is None else f"Rescue report with id {report_id} has already been processed"
        super().__init__(status_code=400, detail=message)


# Notification Exceptions



class NotificationError(HTTPException):
    
    pass


class NotificationNotFoundError(NotificationError):
    def __init__(self, notif_id=None):
        message = "Notification not found" if notif_id is None else f"Notification with id {notif_id} not found"
        super().__init__(status_code=404, detail=message)


class NotificationCreationError(NotificationError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create notification: {error}")



# Store Exceptions



class StoreError(HTTPException):
    pass

class StoreItemNotFoundError(StoreError):
    def __init__(self, item_id=None):
        message = "Store item not found" if item_id is None else f"Item with id {item_id} not found"
        super().__init__(status_code=404, detail=message)

class OrderCreationError(StoreError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create order: {error}")






# Lost & Found Exceptions

class LostFoundError(HTTPException):
    
    pass

class LostFoundNotFoundError(LostFoundError):
    def __init__(self, report_id=None):
        message = "Lost & Found report not found" if report_id is None else f"Lost & Found report with id {report_id} not found"
        super().__init__(status_code=404, detail=message)

class LostFoundCreationError(LostFoundError):
    def __init__(self, error: str):
        super().__init__(status_code=500, detail=f"Failed to create lost & found report: {error}")




class AuthorizationError(Exception):
    pass

class ChatError(HTTPException):
    pass

class ChatNotFoundError(ChatError):
    def __init__(self, chat_id=None):
        message = "Chat not found" if chat_id is None else f"Chat with id {chat_id} not found"
        super().__init__(status_code=404, detail=message)


class ChatMemberExistsError(ChatError):
    def __init__(self):
        message = "User is already a member of the chat"
        super().__init__(status_code=400, detail=message)