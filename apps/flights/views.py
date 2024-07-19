from django.shortcuts import render,redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import FlightSearchSerializer
import json
from rest_framework.decorators import api_view
import pytz
import requests
from django.utils import timezone
import datetime
from django.http import HttpResponse
from .models import Reservation,BookerInfo,PassengerInfo
from dotenv import load_dotenv
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# load_dotenv(os.path.join(BASE_DIR, '.env'))

load_dotenv()  # 환경 변수 파일 로드

# 환경 변수 로드
api_key = os.getenv('FLIGHTS_API_KEY')
api_secret = os.getenv('FLIGHTS_API_SECRET')

class Flights_Search(APIView):
    def post(self, request):
        print("Raw Request Data:", request.data)  # 데이터 확인용 출력

        # 데이터를 복사하여 수정 가능한 객체로 만듭니다.
        request_data = request.data.copy()

        # Convert oneWay to boolean
        if isinstance(request_data['oneWay'], str):
            request_data['oneWay'] = request_data['oneWay'].lower() == 'true' #자바스크립트는 true or false
        else:
            request_data['oneWay'] = bool(request_data['oneWay'])
        
        print("Converted Request Data:", request_data)  # 변환된 데이터 확인용 출력

        serializer = FlightSearchSerializer(data=request_data)
        if serializer.is_valid():
            data = serializer.validated_data
            origin = data['origin']
            destination = data['destination']
            departure_date = data['departure_date']
            one_way = data['oneWay']
            adults = data['adults']
            children = data['children']
            infants = data['infants']

            auth_url = 'https://test.api.amadeus.com/v1/security/oauth2/token'
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': api_key,
                'client_secret': api_secret
            }
            
            auth_response = requests.post(auth_url, data=auth_data)
            if auth_response.status_code != 200:
                return Response({'error': 'Failed to authenticate with Amadeus API'}, status=auth_response.status_code)
            
            auth_response_data = auth_response.json()
            access_token = auth_response_data.get('access_token')
            
            if not access_token:
                return Response({'error': 'Failed to retrieve access token'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            search_url = 'https://test.api.amadeus.com/v2/shopping/flight-offers'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            # --------------------------------------------------------
            if adults + children + infants >= 10:
                return Response({'error': '예약인원은 최대 9명입니다.'}, status=status.HTTP_400_BAD_REQUEST)

            
            def search_flights(origin, destination, departure_date):
                params = {
                    'originLocationCode': origin,
                    'destinationLocationCode': destination,
                    'departureDate': departure_date.strftime('%Y-%m-%d'),
                    'adults': adults,
                    'children': children,
                    'infants': infants,
                    'nonStop': 'true',
                    'max': 30,
                }
                print("Search Params:", params)  # 요청 파라미터 확인용 출력

                response = requests.get(search_url, headers=headers, params=params)
                if response.status_code == 200:
                    flights_data = response.json()
                    print("Response Data:", flights_data)  # 응답 데이터 확인용 출력
                    return flights_data
                else:
                    return None
            
            def get_exchange_rate(from_currency='EUR', to_currency='KRW'): #환율 API 사용 
                exchange_rate_api_url = f'https://api.exchangerate-api.com/v4/latest/{from_currency}'
                response = requests.get(exchange_rate_api_url)
                if response.status_code == 200:
                    rates = response.json().get('rates', {})
                    return rates.get(to_currency, 1300)  # 기본 환율을 1300으로 설정
                else:
                    return 1300

            def convert_currency(amount, exchange_rate): # 소수점 제거
                return int(amount * exchange_rate)  

            def convert_time_to_kst(utc_time_str): #한국 시간으로 변환 
                utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S')
                utc_time = utc_time.replace(tzinfo=pytz.utc)
                kst_time = utc_time.astimezone(pytz.timezone('Asia/Seoul'))
                return kst_time.strftime('%Y-%m-%d %H:%M:%S')
            
            def process_flights_data(flights_data, exchange_rate):
                for flight in flights_data.get('data', []):
                    # 가격 변환
                    flight['price']['total'] = convert_currency(float(flight['price']['total']), exchange_rate)
                    flight['price']['base'] = convert_currency(float(flight['price']['base']), exchange_rate)
                    flight['price']['currency'] = 'KRW'
                    
                    # 개별 여행자 가격 변환
                    for traveler_pricing in flight.get('travelerPricings', []):
                        traveler_pricing['price']['total'] = convert_currency(float(traveler_pricing['price']['total']), exchange_rate)
                        traveler_pricing['price']['base'] = convert_currency(float(traveler_pricing['price']['base']), exchange_rate)
                        traveler_pricing['price']['currency'] = 'KRW'
                    
                    # 시간 변환
                    for itinerary in flight.get('itineraries', []):
                        for segment in itinerary.get('segments', []):
                            segment['departure']['at'] = convert_time_to_kst(segment['departure']['at'])
                            segment['arrival']['at'] = convert_time_to_kst(segment['arrival']['at'])
                return flights_data

            exchange_rate = get_exchange_rate()

            if one_way:
                flights_data = search_flights(origin, destination, departure_date)
                if flights_data:
                    flights_data = process_flights_data(flights_data, exchange_rate)
                    return Response(flights_data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Failed to retrieve flight offers'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                departure_flights_data = search_flights(origin, destination, departure_date)
                return_date = data['return_date']
                return_flights_data = search_flights(destination, origin, return_date)
                
                if departure_flights_data and return_flights_data:
                    departure_flights_data = process_flights_data(departure_flights_data, exchange_rate)
                    return_flights_data = process_flights_data(return_flights_data, exchange_rate)
                    combined_data = {
                        'departure_flights': departure_flights_data,
                        'return_flights': return_flights_data,
                    }
                    return Response(combined_data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Failed to retrieve flight offers'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            print("Serializer Errors:", serializer.errors)  # 직렬화 오류 출력
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def flight_search_view(request):
    return render(request, 'flights/flight_search.html')

def flight_details_view(request, flight_id):
    flight_data = request.GET.get('flight')
    
    if flight_data:
        try:
            flight = json.loads(flight_data)
        except json.JSONDecodeError:
            flight = None
    else:
        flight = None

    outbound_segments = []
    return_segments = []
    stop_info_outbound = '정보 없음'
    stop_info_return = '정보 없음'
    traveler_pricings_outbound = []
    traveler_pricings_return = []

    if flight:
        if 'outbound' in flight and flight['outbound']:
            outbound_segments = flight['outbound']['itineraries'][0]['segments']
            number_of_stops_outbound = len(outbound_segments) - 1
            stop_info_outbound = f'{number_of_stops_outbound} stops' if number_of_stops_outbound > 0 else 'Non-stop'
            traveler_pricings_outbound = flight['outbound'].get('travelerPricings', [])

        if 'return' in flight and flight['return']:
            return_segments = flight['return']['itineraries'][0]['segments']
            number_of_stops_return = len(return_segments) - 1
            stop_info_return = f'{number_of_stops_return} stops' if number_of_stops_return > 0 else 'Non-stop'
            traveler_pricings_return = flight['return'].get('travelerPricings', [])

    return render(request, 'flights/flight_details.html', {
        'flight': flight,
        'stop_info_outbound': stop_info_outbound,
        'stop_info_return': stop_info_return,
        'traveler_pricings_outbound': traveler_pricings_outbound,
        'traveler_pricings_return': traveler_pricings_return
    })

def flight_booking_view(request):
    if request.method == 'GET':
        flight_data = request.GET.get('flight')
        flight = json.loads(flight_data) if flight_data else None
        number_people = len(flight['traveler_pricings']) if flight else 0
        return render(request, 'flights/book.html', {'flight': flight, 'number_people': number_people})

    elif request.method == 'POST':
        try:
            flight_data = request.POST.get('flight')
            print("Raw flight data:", flight_data)
            flight = json.loads(flight_data) if flight_data else None
            print("Parsed flight data:", flight)

            passengers_data = request.POST.get('passengers')
            print("Raw passengers data:", passengers_data)

            if passengers_data:
                passengers = json.loads(passengers_data)
                print("Parsed passengers data:", passengers)
            else:
                return HttpResponse('탑승자 데이터가 없습니다.', status=400)

            # 현재 날짜를 예약 날짜로 설정 (timezone-aware)
            reservation_date = timezone.now()
            number_of_people = len(flight['traveler_pricings'])

            valid_itineraries = [itinerary for itinerary in flight['itineraries'] if itinerary['segments']]

            if not valid_itineraries:
                return HttpResponse('유효한 일정이 없습니다.', status=400)

            reservation = None

            # 편도일 때
            if len(valid_itineraries) == 1:
                try:
                    segment = valid_itineraries[0]['segments'][0]
                    reservation = Reservation(
                         user=request.user,
                        reservation_date=reservation_date,
                        number_of_people=number_of_people,
                        departure_airport=segment['departure']['iataCode'],
                        arrival_airport=segment['arrival']['iataCode'],
                        departure_time =segment['departure']['at'] ,
                        arrival_time =segment['arrival']['at'] ,
                        flight_number=segment['number'],
                        airline_code=segment['carrierCode'],
                        flight_name=f"{segment['carrierCode']} {segment['number']}",
                        free_baggage_allowance=int(float(flight['traveler_pricings'][0]['fareDetailsBySegment'][0].get('includedCheckedBags', {}).get('weight', 0)))
                    )
                    reservation.save()
                except KeyError as e:
                    print(f'Missing key in flight data: {e}')
                    return HttpResponse(f'항공편 데이터에 누락된 키가 있습니다: {e}', status=400)
            elif len(valid_itineraries) == 2:  # 왕복일 때
                try:
                    outbound_segment = valid_itineraries[0]['segments'][0]
                    return_segment = valid_itineraries[1]['segments'][0]
                    reservation = Reservation(
                        user=request.user,
                        reservation_date=reservation_date,
                        number_of_people=number_of_people,
                        departure_airport=outbound_segment['departure']['iataCode'],
                        arrival_airport=outbound_segment['arrival']['iataCode'],
                        departure_time =outbound_segment['departure']['at'] ,
                        arrival_time =outbound_segment['arrival']['at'] ,
                        flight_number=outbound_segment['number'],
                        airline_code=outbound_segment['carrierCode'],
                        flight_name=f"{outbound_segment['carrierCode']} {outbound_segment['number']}",
                        free_baggage_allowance=int(float(flight['traveler_pricings'][0]['fareDetailsBySegment'][0].get('includedCheckedBags', {}).get('weight', 0))),
                        return_departure_airport=return_segment['departure']['iataCode'],
                        return_arrival_airport=return_segment['arrival']['iataCode'],
                        return_depature_time =return_segment['departure']['at'] ,
                        return_arrival_time = return_segment['arrival']['at'],
                        return_flight_number=return_segment['number'],
                        return_airline_code=return_segment['carrierCode'],
                        return_flight_name=f"{return_segment['carrierCode']} {return_segment['number']}",
                        return_free_baggage_allowance=int(float(flight['traveler_pricings'][0]['fareDetailsBySegment'][0].get('includedCheckedBags', {}).get('weight', 0))),
                    )
                    reservation.save()
                except KeyError as e:
                    print(f'Missing key in flight data: {e}')
                    return HttpResponse(f'항공편 데이터에 누락된 키가 있습니다: {e}', status=400)

            if reservation:
                # 예약자 정보 저장
                booker_info = BookerInfo(
                    reservation=reservation,
                    name=request.POST.get('name'),
                    phone_number=request.POST.get('phone_number'),
                    email=request.POST.get('email'),
                )
                booker_info.save()

                # 탑승자 정보 저장
                for passenger in passengers:
                    traveler_pricing = next((tp for tp in flight['traveler_pricings'] if tp['travelerId'] == passenger['traveler_id']), None)
                    if traveler_pricing:
                        one_way_price = int(float(traveler_pricing['price']['base']))
                        return_price = int(float(traveler_pricing['price']['base'])) if len(valid_itineraries) == 2 else 0
                        age_category = traveler_pricing['travelerType']

                        passenger_info = PassengerInfo(
                            reservation=reservation,
                            last_name=passenger['last_name'],
                            first_name=passenger['first_name'],
                            gender=passenger['gender'],
                            nationality=passenger.get('nationality', '대한민국'),
                            one_way_price=one_way_price,
                            return_price=return_price,
                            age_category=age_category,
                            birth_date = passenger['birth_date']
                        )
                        passenger_info.save()

                return redirect('/')
            else:
                return HttpResponse('예약을 생성하는 중 오류가 발생했습니다.', status=400)

        except json.JSONDecodeError as e:
            print(f'JSON Decode Error: {e}')
            return HttpResponse(f'JSON Decode Error: {e}', status=400)
        except Exception as e:
            print(f'예약 처리 중 오류가 발생했습니다: {e}')
            return HttpResponse(f'예약 처리 중 오류가 발생했습니다: {e}', status=500)
