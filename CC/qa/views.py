from django.shortcuts import render, redirect, get_object_or_404
from .models import Question
from .forms import QuestionForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# Create your views here.
def questions(request):
 questions = Question.objects.all()
 questions_count=Question.objects.count()
 context={
    'questions': questions,
    'questions_count': questions_count,
    }
 print(questions_count)
 return render(request, 'qa/Questions_List.html',context)
def questionDetailView(request, pk,):  # slug):
    data = get_object_or_404(Question, pk=pk)
    context = {
        'data': data,
    }
    print(data.body)
    print(data)
    return render(request, 'qa/questionDetailView.html', context)





    
    
@login_required
def new_question(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
                print("valid form")
                formTags = form.cleaned_data['tags']
                gettingBody = form.cleaned_data['body']
                gettingTitle = form.cleaned_data['title']
                new_post = form.save(commit=False)
                new_post.post_owner = request.user
                if len(gettingBody) >= 0 and len(gettingBody) <= 29:
                            messages.error(
                                request, "Body Text should atleast 30 words. You entered " + str(len(gettingBody)))
                elif len(gettingTitle) >= 0 and len(gettingTitle) <= 14:
                            messages.error(
                                request, "Title must be at least 15 characters.")
                else:
                            print(form.errors)
                            form.save()
                            form.save_m2m()
                            return redirect('qa:questions')           
    else:
        print("else")
        form = QuestionForm()

    context = {'form': form}
    return render(request, 'qa/new_question.html', context)

def reviewQuestion(request):
        #AllTags = Tag.objects.all().values_list('name', flat=True)
        post_title = request.GET.get('title', None)
        post_body = request.GET.get('body', None)
        formTags = request.GET.get('tags', None)
        taken = Question.objects.filter(title__iexact=post_title).exists()
        formTags = formTags.split(",")
        print(formTags)
        # for typedTags in formTags:
        #     check_if_everything_is_fine = all(
        #         typedTags in AllTags for typedTags in formTags)
        #     define = ''
        #     showNewTagError = False
        #     if request.user.profile.create_tags:
        #         print("No Restrictions")
        #     else:
        #         if not check_if_everything_is_fine:
        #             showNewTagError = True
        #         else:
        #             showNewTagError = False
        #             define = True
        # # print(check_if_everything_is_fine)

        counting = len(post_body)
        if counting >= 0 and counting <= 29:
            postBody = True
            print("Body Text should atleast 30 words. You entered " + str(counting))
            # USED "str(counting)" BECAUSE WITHOUT ADDING str, It would show 'TypeError' :-:
            # print("Body Text should atleast 30 words. You entered " + int(counting))
            # TypeError: can only concatenate str (not "int") to str
        else:
            postBody = False
            print("Body Text is FulFilled")

        # using list comprehension to
        # perform removal
        new = [i for i in formTags if i]

        # spliting = formTags.split(",")
        # print(len(spliting))
        # lengthing = len(spliting)
        # print(lengthing)
        # for words in spliting:
        #     print(count(words))

        if len(new) < 1:
            print("Fine")
            showError = True
        else:
            print("Raise the Error")
            showError = False

        if len(post_title) <= 5:
            print("Add atleast 2 more Words")
            showLessTitleError = True
        else:
            showLessTitleError = False
        # print(showLessTitleError)
        # if taken == True:
        #     is_it_true = True
        # else:
        #     is_it_true = False

        if taken == False and showError == False  and showLessTitleError == False and postBody == False:
            allClear = True
            print("Everything Clear")
        else:
            allClear = False
            print("Something is Missing")

        data = {
            'taken': taken,
            # 'postBody':postBody,
            'showError': showError,
            'allClear': allClear,
        }

        if taken:
            data['error_message_of_title'] = f'Already Existed'
        elif postBody:
            data['error_message_of_body_text'] = f'Words are less than 15'
        elif data['showError']:
            data['error_message_of_tag'] = f'Add atleast One Tag'
        return JsonResponse(data)