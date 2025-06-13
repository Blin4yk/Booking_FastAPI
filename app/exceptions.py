from fastapi import HTTPException, status

class BookingException(HTTPException):
    status_code = 500 # <-- задаем значения по умолчанию
    detail = ""
    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

class UserAlreadyExistsException(BookingException): # <-- обязательно
    status_code=status.HTTP_409_CONFLICT
    detail="Пользователь уже существует"

class IncorrectEmailOrPassword(BookingException): # <-- обязательно
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Не правильный логин или пароль"

class TokenExpiredException(BookingException): # <-- обязательно
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен истёк"

class TokenAbsentException(BookingException): # <-- обязательно
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Токен отстутсвует"

class IncorrectTokenFormatException(BookingException): # <-- обязательно
    status_code=status.HTTP_401_UNAUTHORIZED
    detail="Неверный формат токена"

class UserIsNotPresent(BookingException): # <-- обязательно
    status_code=status.HTTP_401_UNAUTHORIZED

class RoomCanNotBeBooked(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Не осталось свободных номеров"

class BookingCanNotDelete(BookingException):
    status_code=status.HTTP_409_CONFLICT
    detail="Нельзя отменить бронь"

class HotelIsAbsent(BookingException):
    status_code=status.HTTP_404_NOT_FOUND
    detail="Отеля не существует"