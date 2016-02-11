from .forms import *
from django.views.generic import View, TemplateView
from django.views.generic.edit import FormView

import calendar
from django.db.models import Sum,Count
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from datetime import datetime , timedelta, date
from django.utils.decorators import method_decorator
from django.shortcuts import render_to_response, render, redirect
from tracking.models import Referral,Physician, Organization, LAST_MONTH, LAST_12_MONTH
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

class IndexView(View):
    # display the Organization form
    # template_name = "index.html"
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):

        orgform = OrganizationForm()
        phyform = PhysicianForm()
        refform = ReferralForm()

        today_date = datetime.now().date()
        start_date = today_date - timedelta(days=365)
        end_date = today_date - timedelta(days=1)

        physician_visit_sum = Physician.objects.filter(
            Referral__visit_date__range=(start_date,end_date)).annotate(
            total_visits=Sum('Referral__visit_count')
            ).order_by('-total_visits')[:10]

        org_visit_sum =  Organization.objects.filter(
            Physician__Referral__visit_date__range=(start_date,end_date)).annotate(
            total_org_visits=Sum('Physician__Referral__visit_count')
            ).order_by('-total_org_visits')[:5]

        special_visit_sum =  Organization.objects.filter(org_special=True).filter(
            Physician__Referral__visit_date__range=(start_date,end_date)).annotate(
            total_org_special_visits=Sum('Physician__Referral__visit_count')
            ).order_by('-total_org_special_visits')[:5]

        referrals = Referral.objects.filter(visit_date__range=[LAST_12_MONTH,LAST_MONTH])

        if referrals:
            try:
                referrals = referrals.extra(select={'month': 'STRFTIME("%m",visit_date)'})
                print (referrals[0].month)
            except:
                referrals = referrals.extra(select={'month': 'EXTRACT(month FROM visit_date)'})
            referrals = referrals.values('month').annotate(total_visit_count=Sum('visit_count'))

            for referral in referrals:
                if LAST_MONTH.month <= int(referral['month']) :
                    current_month = date(day=LAST_MONTH.day, month= int(referral['month']), year=LAST_MONTH.year)
                else:
                    current_month = date(day=LAST_12_MONTH.day, month= int(
                        referral['month']), year=LAST_12_MONTH.year)

                last_month = current_month-timedelta(days=364)
                referrals_year = Referral.objects.filter(
                    visit_date__range=[last_month, current_month]).aggregate(year_total=Sum('visit_count'))
                referral['year_total'] = referrals_year['year_total']
                referral['year_from'] = last_month
                referral['year_to'] = current_month
        today = date.today()
        week_ago = today - timedelta(days=7)
        all_orgs = Physician.objects.order_by('physician_name')
        all_ref = {}
        for phys in all_orgs :
            phys_ref = phys.get_referral({'from_date' : week_ago, 'to_date' : today});
            if phys_ref.count() :
                for ref in phys_ref :
                    if not phys.id in all_ref : 
                        all_ref[phys.id] = {'name' : phys.physician_name, 'refs' :  [ ref ] }
                    else :
                        all_ref[phys.id]['refs'].append(ref)

        ctx = {
            "orgform": orgform,
            "phyform": phyform,
            "refform": refform,
            "physician_visit_sum": physician_visit_sum,
            "org_visit_sum": org_visit_sum,
            "special_visit_sum": special_visit_sum,
            "referrals":referrals,
            "all_orgs" : all_ref,
            'today': today,
            'week_ago' : week_ago,
            }
        return render(request,"index.html",ctx )

    def post(self, request, *args, **kwargs):

        phyform = PhysicianForm()
        orgform = OrganizationForm()
        refform = ReferralForm()

        if 'phyform' in request.POST:
            phyform = PhysicianForm(request.POST)
            if phyform.is_valid():
                phyform.save()
                return redirect(reverse('index'))

        elif 'orgform' in request.POST:
            orgform = OrganizationForm(request.POST)
            if orgform.is_valid():
                orgform.save()
                return redirect(reverse('index'))

        elif 'refform' in request.POST:
            refform = ReferralForm(request.POST)
            if refform.is_valid():
                refform.save()
                return redirect(reverse('index'))

        ctx = {
            "orgform": orgform,
            "phyform": phyform,
            "refform": refform,
          }

        return render(request,"index.html",ctx )

class OrganizationView(View):
    # display the Organization form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = OrganizationForm()
        ctx = {"form": form}
        return render(request,"tracking/organization.html",ctx )

    def post(self, request, *args, **kwargs):
        form = OrganizationForm(request.POST)
        ctx = {"form": form}
        if form.is_valid():
            form.save()
            return redirect(reverse('add-physician'))

        return render(request,"tracking/organization.html",ctx )


class PhysicianView(View):
    # display the physician form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = PhysicianForm()
        ctx = {"form": form}
        return render(request,"tracking/physician.html",ctx )


    def post(self, request, *args, **kwargs):
        form = PhysicianForm(request.POST)
        if form.is_valid():
            form.save()
            form = PhysicianForm()

        ctx = {"form": form}
        return render(request,"tracking/physician.html",ctx )


class ReferralView(View):
    # display the referral form
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        form = ReferralForm()
        ctx = {"form": form}
        return render(request,"tracking/referral.html",ctx )

    def post(self, request, *args, **kwargs):
        form = ReferralForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/add/referral/')
        ctx = {"form": form}
        return render(request,"tracking/referral.html",ctx )

class GetReferralReport(View):
    """
    Display a summary of referrals by Organization:provider:
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        all_orgs = Organization.objects.all().order_by('org_name')
        today = datetime.now().date()
        last_year = today.year - 1
        ctx = {
                'all_orgs': all_orgs,
                'last_year':last_year,
            }
        return render(request,"tracking/show_referral_report.html",ctx )


class LogoutView(View):

    def get(self, request, *args, **kwargs):
        auth_logout(request)
        return redirect('/')

class GetReferralHistory(View):
    """
    Display a summary of referrals by Organization:provider:
    """
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        today = date.today()
        week_ago = today - timedelta(days=7)
        all_orgs = Physician.objects.order_by('physician_name')
        all_ref = {}
        for phys in all_orgs :
            phys_ref = phys.get_referral({'from_date' : week_ago, 'to_date' : today});
            if phys_ref.count() :
                for ref in phys_ref :
                    if not phys.id in all_ref : 
                        all_ref[phys.id] = {'name' : phys.physician_name, 'refs' :  [ ref ] }
                    else :
                        all_ref[phys.id]['refs'].append(ref)
                
        form = ReferralHistoryForm(initial={'from_date': week_ago, 'to_date' : today})
        ctx = {
                'all_orgs': all_ref,
                'today': today,
                'week_ago' : week_ago,
                "form": form
            }
        return render(request,"tracking/show_referral_history.html",ctx )
    
    
    def post(self, request, *args, **kwargs):
        
        today = datetime.strptime(request.POST['to_date'], "%Y-%m-%d").date()
        week_ago = datetime.strptime(request.POST['from_date'], "%Y-%m-%d").date()
        form = ReferralHistoryForm(request.POST)
        form.is_valid()
        if 'physician' in request.POST : 
            all_orgs = Physician.objects.filter(id=int(request.POST['physician'])).order_by('physician_name')
        else :
            all_orgs = []
        
        all_ref = {}
        for phys in all_orgs :
            phys_ref = phys.get_referral({'from_date' : week_ago, 'to_date' : today});
            if phys_ref.count() :
                for ref in phys_ref :
                    if not phys.id in all_ref : 
                        all_ref[phys.id] = {'name' : phys.physician_name, 'refs' :  [ ref ] }
                    else :
                        all_ref[phys.id]['refs'].append(ref)
        ctx = {
            'all_orgs': all_ref,
            'today': today,
            'week_ago' : week_ago,
            "form": form
        }
        return render(request,"tracking/show_referral_history.html",ctx )
