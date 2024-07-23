from django import forms
from .models import Review, Reservation
from apps.userinfo.models import User

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = [ 'rating', 'travel_date','content', 'image_url']
        # widgets = {
        #     'rating': forms.RadioSelect(choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')]),
        # }
        widgets = {
            'rating': forms.RadioSelect(choices=[
                (1, '1 Star'),
                (2, '2 Stars'),
                (3, '3 Stars'),
                (4, '4 Stars'),
                (5, '5 Stars')
            ]),
        }

from .models import Reservation, ReservationHolderInfo, GuestInfo, TransportationInfo

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['check_in', 'check_out', 'cancellation_policy_agreed', 'terms_and_conditions_agreed', 'guests_adult', 'guests_child', 'telnum']


class ReservationHolderInfoForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    telnum = forms.CharField(max_length=15)

    class Meta:
        model = ReservationHolderInfo
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ReservationHolderInfoForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['username'].initial = user.username
            self.fields['email'].initial = user.email

class GuestInfoForm(forms.ModelForm):
    class Meta:
        model = GuestInfo
        fields = ['name', 'birth_date', 'gender']

class TransportationInfoForm(forms.ModelForm):
    class Meta:
        model = TransportationInfo
        fields = ['public_transport', 'walking', 'personal_car']