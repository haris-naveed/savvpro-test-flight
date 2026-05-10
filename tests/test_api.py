def test_get_flights(client):
    response = client.get("/flights")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_search_by_origin(client):
    response = client.get("/flights/search", params={"origin": "testorigin"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(f["origin"] == "TestOrigin" for f in data)


def test_book_flight_success(client):
    response = client.post(
        "/bookings",
        json={
            "flight_id": 2,
            "passenger_name": "Alice Smith",
            "passport_number": "AB12345",
            "seat_number": "10A",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert "booking_reference" in body
    assert len(body["booking_reference"]) == 8
    assert body["status"] == "confirmed"
    assert body["flight_id"] == 2


def test_overbooking_blocked(client):
    first = client.post(
        "/bookings",
        json={
            "flight_id": 1,
            "passenger_name": "First Passenger",
            "passport_number": "PP11111",
            "seat_number": "1A",
        },
    )
    assert first.status_code == 201

    second = client.post(
        "/bookings",
        json={
            "flight_id": 1,
            "passenger_name": "Second Passenger",
            "passport_number": "PP22222",
            "seat_number": "1B",
        },
    )
    assert second.status_code == 409
    assert second.json()["detail"] == "No seats available on this flight"


def test_cancel_booking(client):
    before = client.get("/flights/2").json()
    assert before["available_seats"] == 5

    book = client.post(
        "/bookings",
        json={
            "flight_id": 2,
            "passenger_name": "Bob Jones",
            "passport_number": "XY99999",
            "seat_number": "3C",
        },
    )
    assert book.status_code == 201
    ref = book.json()["booking_reference"]

    after_book = client.get("/flights/2").json()
    assert after_book["available_seats"] == 4

    cancel = client.delete(f"/bookings/{ref}")
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"

    after_cancel = client.get("/flights/2").json()
    assert after_cancel["available_seats"] == 5


def test_cancel_twice(client):
    book = client.post(
        "/bookings",
        json={
            "flight_id": 2,
            "passenger_name": "Carol Day",
            "passport_number": "ZZ88888",
            "seat_number": "4D",
        },
    )
    assert book.status_code == 201
    ref = book.json()["booking_reference"]

    first = client.delete(f"/bookings/{ref}")
    assert first.status_code == 200

    second = client.delete(f"/bookings/{ref}")
    assert second.status_code == 409
    assert second.json()["detail"] == "Booking is already cancelled"
