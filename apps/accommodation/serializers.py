# serializers.py
from rest_framework import serializers
from .models import GuestInfo, TransportationInfo, Reservation, Room, Accommodation, Review, ReservationHolderInfo
from apps.userinfo.models import User

# class GuestInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = GuestInfo
#         fields = '__all__'

# class TransportationInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = TransportationInfo
#         fields = '__all__'

# class PaymentDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = PaymentDetail
#         fields = '__all__'

# class ReservationSerializer(serializers.ModelSerializer):
#     guest_info = GuestInfoSerializer()
#     transportation_info = TransportationInfoSerializer()
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     reservation_holder_info = serializers.PrimaryKeyRelatedField(queryset=ReservationHolderInfo.objects.all())
#     # payment_detail = PaymentDetailSerializer()

#     class Meta:
#         model = Reservation
#         fields = '__all__'

#     def create(self, validated_data):
#         guest_info_data = validated_data.pop('guest_info')
#         transportation_info_data = validated_data.pop('transportation_info')
#         # payment_detail_data = validated_data.pop('payment_detail')

#         guest_info = GuestInfo.objects.create(**guest_info_data)
#         transportation_info = TransportationInfo.objects.create(**transportation_info_data)
#         # payment_detail = PaymentDetail.objects.create(**payment_detail_data)

#         reservation = Reservation.objects.create(
#             guest_info=guest_info,
#             transportation_info=transportation_info,
#             reservation_amount=validated_data['reservation_amount'],
#             total_amount=validated_data['total_amount'],
#             check_in=validated_data['check_in'],  # 올바른 필드 이름 사용
#             check_out=validated_data['check_out'],  # 올바른 필드 이름 사용
#             guests=validated_data['guests'],
#             **validated_data
#         )

#         return reservation

# class ReservationSerializer(serializers.ModelSerializer):
#     guest_info = GuestInfoSerializer()
#     transportation_info = TransportationInfoSerializer()
#     user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
#     reservation_holder_info = serializers.PrimaryKeyRelatedField(queryset=ReservationHolderInfo.objects.all())

#     class Meta:
#         model = Reservation
#         fields = '__all__'

#     def create(self, validated_data):
#         guest_info_data = validated_data.pop('guest_info')
#         transportation_info_data = validated_data.pop('transportation_info')

#         guest_info = GuestInfo.objects.create(**guest_info_data)
#         transportation_info = TransportationInfo.objects.create(**transportation_info_data)

#         reservation = Reservation.objects.create(
#             guest_info=guest_info,
#             transportation_info=transportation_info,
#             **validated_data
#         )

#         return reservation


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'

class AccommodationSerializer(serializers.ModelSerializer):
    rooms = RoomSerializer(many=True, read_only=True) 
    class Meta:
        model = Accommodation
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'




# from rest_framework import serializers
# from .models import Reservation, GuestInfo, TransportationInfo, User, ReservationHolderInfo

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'telnum', 'email')  # 필요한 필드들을 추가합니다

class ReservationHolderInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ReservationHolderInfo
        fields = ('user',)  # 필요한 필드들을 추가합니다

class GuestInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuestInfo
        fields = '__all__'  # 필요한 필드들을 추가합니다

class TransportationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportationInfo
        fields = '__all__'  # 필요한 필드들을 추가합니다

class ReservationSerializer(serializers.ModelSerializer):
    guest_info = GuestInfoSerializer()
    transportation_info = TransportationInfoSerializer()
    user = UserSerializer()
    reservation_holder_info = ReservationHolderInfoSerializer()

    class Meta:
        model = Reservation
        fields = '__all__'

    # def create(self, validated_data):
    #     guest_info_data = validated_data.pop('guest_info')
    #     transportation_info_data = validated_data.pop('transportation_info')
    #     reservation_holder_info_data = validated_data.pop('reservation_holder_info')
    #     user_data = validated_data.pop('user')

    #     user_serializer = self.fields['user']
    #     reservation_holder_info_serializer = self.fields['reservation_holder_info']

    #     # Create or update nested serializers
    #     user_instance, _ = User.objects.update_or_create(
    #         id=user_data.get('id'),
    #         defaults=user_data
    #     )

        # reservation_holder_info_instance, _ = ReservationHolderInfo.objects.update_or_create(
        #     user=user_instance,
        #     defaults=reservation_holder_info_data
        # )

        # guest_info = GuestInfo.objects.create(**guest_info_data)
        # transportation_info = TransportationInfo.objects.create(**transportation_info_data)

        # reservation = Reservation.objects.create(
        #     guest_info=guest_info,
        #     transportation_info=transportation_info,
        #     reservation_holder_info=reservation_holder_info_instance,
        #     **validated_data
        # )

        # return reservation