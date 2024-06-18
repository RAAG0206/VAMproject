from django.http import HttpResponse, HttpResponseNotFound, FileResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from .models import User
import numpy as np
import os
import vamtoolbox as vam
import vedo
import vedo.vtkclasses as vtki
from vedo import dataurl, Plotter, Volume, Text3D

from .forms import CaptchaForm

# /
def main_view(request):
    if request.method == "GET":
        form = CaptchaForm()
        context = {"form": form}
        return render(request, "index.html", context)
    elif request.method == "POST":
        print("Starting slicing")
        print("=====================================")
        print("=====================================")
        print("=====================================")
        # 250 is the original resolution
        # 125 is another resolution that goes further
        target_geo = vam.geometry.TargetGeometry(stlfilename="VAMapp/static/file.stl", resolution=250)
        print("vam.geometry.TargetGeometry done")
        print("=====================================")
        print("=====================================")
        print("=====================================")
        num_angles = 360
        angles = np.linspace(0, 360 - 360 / num_angles, num_angles)
        proj_geo = vam.geometry.ProjectionGeometry(angles,ray_type='parallel',CUDA=True)
        print("vam.geometry.ProjectionGeometry done")
        print("=====================================")
        print("=====================================")
        print("=====================================")
        optimizer_params = vam.optimize.Options(method='PM',n_iter=50,d_h=0.85,d_l=0.6,filter='hamming')
        print("vam.optimize.Options done")
        print("=====================================")
        print("=====================================")
        print("=====================================")
        opt_sino, opt_recon, error = vam.optimize.optimize(target_geo, proj_geo,optimizer_params)
        print("=====================================")
        print("=====================================")
        print("=====================================")
        print("Svam.optimize.optimize done")
        print(opt_sino.array.shape, opt_recon.array.shape , error.shape)
        print("Processing finished")
        
        return HttpResponse({"hola": "hola"})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')

def export_window(fileoutput, binary=False, plt=None):
    try:
        os.remove("embryo.x3d")
    except:
        print("Nothing happens")

    if plt is None:
        plt = vedo.plotter_instance

    fr = fileoutput.lower()
    if fr.endswith(".x3d"):
        #plt.render()
        exporter = vtki.new("X3DExporter")
        exporter.SetBinary(binary)
        exporter.FastestOff()
        exporter.SetInput(plt.window)
        exporter.SetFileName(fileoutput)
        exporter.Update()
        exporter.Write()
        
        wsize = plt.window.GetSize()
    return plt

# /check_access function to determine if the user is allowed to submit a file
def check_access(request):
    if request.method == "POST":
        allowed = False
        CONNECTIONS_ALLOWED = 2

        user_agent = request.META.get('HTTP_USER_AGENT')
        ip_address = request.META.get('REMOTE_ADDR')
        agent_users = User.objects.filter(user_agent=user_agent)
        ip_users = User.objects.filter(ip_address=ip_address)

        print(user_agent)
        print(ip_address)
        print(type(agent_users))
        print(type(ip_users))
        # print(agent_users)
        # print(ip_users)
        # print(len(agent_users) == 0)
        # print(len(ip_users) == 0)

        """
        Some results might have the same ip address but different user agents, for example 2 users
        from the same network but using different devices (users in house, company, etc). So we need
        to check all the ip address if they have the user's ip address, as well as the user agent.
        """
        

        if len(ip_users) > 0 and len(agent_users) == 0:
            # at least one register of the user's ip address and none of the user agent
            max_connections = max([user.n_connections for user in ip_users])
            for user in ip_users:
                if user.n_connections < CONNECTIONS_ALLOWED:
                    user.n_connections += 1
                    user.last_date_connected = timezone.now()
                    user.save()
            if max_connections < CONNECTIONS_ALLOWED: 
                allowed = True
            print("======================================")
            print("======================================")
            print("======================================")
            print(">0 ips and 0 agents")
            print("======================================")
            print("======================================")
            print("======================================")
        elif len(ip_users) == 0 and len(agent_users) > 0:
            # at least one register of the user's user agent and none of the user's ip address
            max_connections = max([user.n_connections for user in agent_users])
            for user in agent_users:
                if user.n_connections < CONNECTIONS_ALLOWED:
                    user.n_connections += 1
                    user.last_date_connected = timezone.now()
                    user.save()
            if max_connections < CONNECTIONS_ALLOWED: 
                allowed = True
            print("======================================")
            print("======================================")
            print("======================================")
            print("0 ips and >0 agents")
            print("======================================")
            print("======================================")
            print("======================================")
        elif len(ip_users) > 0 and len(agent_users) > 0:
            # at least one register of the user's ip address and the user's user agent
            unique_agent_users = set(agent_users)
            unique_ip_users = set(ip_users)
            unique_users = unique_agent_users.union(unique_ip_users)
            max_connections = max([user.n_connections for user in unique_users])
            for user in unique_users:
                if user.n_connections < CONNECTIONS_ALLOWED:
                    user.n_connections += 1
                    user.last_date_connected = timezone.now()
                    user.save()
                if max_connections < CONNECTIONS_ALLOWED:
                    allowed = True
            print("======================================")
            print("======================================")
            print("======================================")
            print(">0 ips and >0 agents")
            print("======================================")
            print("======================================")
            print("======================================")
        elif len(ip_users) == 0 and len(agent_users) == 0:
            # no register of the user's ip address and the user's user agent (create a new register)
            allowed = True

            date = timezone.now()
            print(date)
            print(type(date))

            
            new_obj = User.objects.create(
                user_agent=user_agent,
                ip_address=ip_address,
                n_connections=1,
                last_date_connected=date
            )
            new_obj.save()
            
            
            print("======================================")
            print("======================================")
            print("======================================")
            print("0 ips and 0 agents")
            print("======================================")
            print("======================================")
            print("======================================")

        return JsonResponse({'allowed': allowed})
    else:
        return HttpResponseNotFound('<h1>Page not found</h1>')