from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.base import Base
from accounts.helpers.decorators import CheckRole

import pandas as pd

from setup.models import PoliceStation,District
from accounts.models import Profile

@login_required(login_url='/login/')
def home(request):
    context = {}
    
    ProcessPoliceStation(request)
    return render(request, 'dataprocess/home.html', context)



def ProcessPoliceStation(request):
    try:
        
        # On Server
        LogPath = 'C:/inetpub/wwwroot/wegscada.com/dahi.wegscada.com/Subscribe/1_Log/'
        # Local
        LogPath = '/Users/ashishpyasi/GITHUB/dial112_hrms_fms/ApplicationDocs/RHQ_Data/'

        fileName = "mp_ps_list.csv"

        df = pd.read_csv(LogPath + fileName)

        district_wise = (
            df.groupby("District")["Police_Station"]
            .apply(list)
            .to_dict()
        )

        profile = Profile.objects.filter(user=request.user).select_related('tenantProfile').first()
        tenant = profile.tenantProfile if profile else None

        for district, stations in district_wise.items():
            print(f"\n{district}:")
            district = District.objects.filter(district_name=district).first()
            for station in stations:
                if not  PoliceStation.objects.filter(police_station_name=station,district=district).exists():
                    print(f" - {station}")
                    policeStation = PoliceStation.objects.create(
                                police_station_name=station,
                                district=district,
                                tenantProfile=tenant,
                                created_by=request.user,
                            )

    except Exception as e:
        print(str(e))