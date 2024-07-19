from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserEditForm

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage')  # 저장 후 다시 프로필 페이지로 리다이렉트
        else:
            messages.error(request, '프로필 업데이트 중 오류가 발생했습니다. 다시 시도해주세요.')
    else:
        form = UserEditForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user,
    }
    return render(request, 'mypage.html', context)
