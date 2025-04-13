from django.shortcuts import render
from .models import Sport

def sport_list(request):
    sports = Sport.objects.all()
    return render(request, 'sports/sport_list.html', {'sports': sports})

# def sport_list(request):
#     # sports = Sport.objects.all()
#     # sports = ['Cricket','Basketball','Volleyball','Pool','Pickleball','Bowling','TableTennis','Badminton']
#     # return render(request, 'sports/sport_list.html', {'sports': sports})
#     return render(request, 'sport_list.html', {'sports': sports})


def sport_detail(request,sport_name):
    # template_name = f'sports/{sport_name}.html'
    template_name = f'{sport_name}.html'
    return render(request, template_name)
