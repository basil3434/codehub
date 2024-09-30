from django.forms import BaseModelForm

from django.http import HttpResponse

from django.shortcuts import render,redirect

from django.urls import reverse,reverse_lazy

from django.views.generic import View,TemplateView,UpdateView,CreateView,DetailView,ListView

from store.forms import  SignUpForm,LoginForm,UserProfileForm,ProjectForm

from django.contrib.auth import authenticate,login,logout

from django.contrib import messages

from store.models import UserProfile,Project,WishListItems,OrderSummary

from django.db.models import Sum



# Create your views here.

class SignupView(View):
    def get(self,request,*args,**kwargs):
        form_instance=SignUpForm
        return render(request,"store/signin.html",{"form":form_instance})
    def post(self,request,*args,**kwargs):

        form_instance=SignUpForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            print("register successfully...")

            messages.success(request,'account created successfuly')

            return redirect("signin")

        else:

            print("registration failed")

            messages.success(request,'account creation failed')

            return render(request,"store/login.html",{"form":form_instance})
        
class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"store/login.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():
             
             data=form_instance.cleaned_data

             user_obj=authenticate(request,**form_instance.cleaned_data)
     
             if user_obj:
     
                 login(request,user_obj)

                 print("successfully...")

                #  messages.success(request,'Login Successfully..!')
     
                 return redirect("index")
             
        print("login failed")

        messages.success(request,'Login failed..!')
            
        return render(request,"store/login.html",{"form":form_instance})

class IndexView(View):

    template_name="store/index.html"

    def get(self,request,*args,**kwargs):

        qs=Project.objects.all().exclude(owner=request.user)

        return render(request,self.template_name,{"projects":qs})

class UserProfileUpdateView(UpdateView):

    model=UserProfile

    form_class=UserProfileForm

    template_name="store/profile_edit.html"

    success_url=reverse_lazy("index")

    # def get_success_url(self) -> str:
        # return reverse("index")

class ProjectCreateView(CreateView):

    model=Project

    form_class=ProjectForm

    template_name="store/project_add.html"

    success_url=reverse_lazy("index")

    def form_valid(self,form):

        print(self.request.user)

        form.instance.owner=self.request.user


        return super().form_valid(form)
    

class ProjectListView(View):

    def get(self,request,*args,**kwargs):

        # qs=Project.objects.filter(owner=request.user)

        qs=request.user.projects.all()

        return render(request,"store/myprojects.html",{"works":qs})


class ProjectDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        Project.objects.get(id=id).delete()

        return redirect("myworks")

class ProjectDetailView(DetailView):

    template_name="store/project_detail.html"

    context_object_name="project"

    model=Project


class AddToWishlistView(View):
    
    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        project_obj=Project.objects.get(id=id)

        WishListItems.objects.create(
                                     wishlist_object=request.user.basket,
                                     
                                     project_object=project_obj)
        
        print("Item has been added to wishlist")

        return redirect("index")


class MyCartView(View):

    def get(self,request,*args,**kwargs):

        qs=request.user.basket.basket_items.filter(is_order_placed=False)

        total=request.user.basket.wishlist_total

        return render(request, "store/wishlist_summary.html",{"cartitems":qs,"total":total})
    
class WishListItemDeleteView(View):

    def get(self,request,*args,**kwargs):

        id=kwargs.get("pk")

        WishListItems.objects.get(id=id).delete()

        return redirect("my-cart")

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt,name="dispatch")
class PaymentVerificationView(View):

    def post(self,request,*args,**kwargs):

        print(request.POST)

        Order_summary_object=OrderSummary.objects.get(order_id=request.POST.get("razorpay_order_id"))

        client = razorpay.Client(auth=("YOUR_ID", "YOUR_SECRET"))

        login(request,Order_summary_object.user_object)

        try:

            
            client.utility.verify_payment_signature(request.POST)

            print("payment success")

            order_id=request.POST.get("razorpay_order_id")

            OrderSummary.object.filter(order_id=order_id).update(is_paid=True)

            cart_items=request.user.basket.basket_items(is_order_placed=False)

            for ci in cart_items:

                ci.is_order_placed=True

                ci.save()

        except:

            print("payment failed")

                                 
        return redirect("index.html")
  
class MyPusrchasingView(View):

    model=OrderSummary

    context_object_name="orders"

    def get(self,request,*args,**kwargs):

        qs=OrderSummary.objects.filter(user_object=request.user, is_paid=True).order_by('created_date')

        return render(request,"store/ordersummary.html",{"orders":qs})

