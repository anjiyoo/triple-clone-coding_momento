from rest_framework import serializers

class FlightSearchSerializer(serializers.Serializer):
    TRIP_TYPE_CHOICES = [
        (True, 'One Way'),
        (False, 'Round Trip'),
    ]
    # TRAVEL_CLASS_CHOICES = [
    #     ('ECONOMY', 'Economy'),
    #     ('BUSINESS', 'Business'),
    # ]

    origin = serializers.CharField(max_length=3)  # 출발지 IATA 코드
    destination = serializers.CharField(max_length=3)  # 도착지 IATA 코드
    departure_date = serializers.DateField()  # 출발 날짜
    return_date = serializers.DateField(required=False, allow_null=True)  # 귀국 날짜 (왕복일 경우 필요)
    oneWay = serializers.BooleanField()  # 여행 유형 (편도 또는 왕복)
    adults = serializers.IntegerField(default=1)  # 성인 승객 수 (기본값 1)
    children = serializers.IntegerField(default=0)  # 소아 승객 수 (기본값 0)
    infants = serializers.IntegerField(default=0)  # 유아 승객 수 (기본값 0)
    # cabin_class = serializers.ChoiceField(choices=TRAVEL_CLASS_CHOICES, default='ECONOMY')  # 좌석 등급

    def validate(self, data):
        if data['oneWay'] == False and not data.get('return_date'):
            raise serializers.ValidationError("Return date is required for roundtrip.")
        return data
