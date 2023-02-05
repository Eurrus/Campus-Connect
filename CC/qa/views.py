from django.shortcuts import render, redirect, get_object_or_404
from .models import Question,Answer
from .forms import QuestionForm,AnswerForm,EditAnswerForm,UpdateQuestion
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import QUpvote,QDownvote
from datetime import timedelta
from review.models import FlagPost
from review.forms import FlagQuestionForm
from django.db.models import  Q
from django.core.mail import send_mail,mail_admins
# Create your views here.
def questions(request):
 questions = Question.objects.all()
 questions_count=Question.objects.count()
 context={
    'questions': questions,
    'user':request.user,
    }

 return render(request, 'qa/Questions_List.html',context)
def questionDetailView(request, pk,):  # slug):
    data = get_object_or_404(Question, pk=pk)
    #answers_of_questions = data.answer_set.all()
    sorted(data.answer_set.all(),key=lambda m: m.countAllTheVotes)
    ratings_tuples = [(r.id, r.countAllTheVotes) for r in data.answer_set.all()]  
    ratings_list = sorted(ratings_tuples, key = lambda x: x[1]) 
    answers_of_questions = ratings_list
    print(answers_of_questions)
    STORING_THE_ORIGINAL = []
    for anss in answers_of_questions:
        STORING_THE_ORIGINAL.append(anss)
    page = request.GET.get('page', 1)

    paginator = Paginator(STORING_THE_ORIGINAL, 10)
    try:
        answers = paginator.page(page)
    except PageNotAnInteger:
        answers = paginator.page(1)
    except EmptyPage:
        answers = paginator.page(paginator.num_pages)
    if request.method == 'POST':
        form = AnswerForm(data=request.POST)
        if form.is_valid():
            gettingBody = form.cleaned_data['body']
            new_post = form.save(commit=False)
            new_post.answer_owner = request.user
            new_post.questionans = data
            data.active_date = timezone.now()
            data.save()
            new_post.save()
            #print(gettingBody)
    else:
        form=AnswerForm()  
        print("hola") 
        # return render(request, 'qa/questionDetailView.html')    
    context = {
        'data': data,
        'form' : form,
        'answers':answers
    }
    return render(request, 'qa/questionDetailView.html', context)
def delete_answer(request, answer_id):
    """
    view to delete Answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.answer_owner:
        answer.is_deleted=True
        answer.save()
        return redirect('qa:questionDetailView', pk=answer.questionans.id)
    else:
        messages.error(request, 'You are not post owner')
        return redirect('qa:questionDetailView', pk=answer.questionans.id)
def undelete_answer(request, answer_id):
    """
    view to undelete Answer
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.answer_owner:
        answer.is_deleted = False
        answer.save()
        return redirect('qa:questionDetailView', pk=answer.questionans.id)
    else:
        messages.error(request, 'You are not post owner')
        return redirect('qa:questionDetailView', pk=answer.questionans.id)
def deleteQuestion(request, question_id):
    """
    view to delete question and award badges if user is eligible
    """
    question = get_object_or_404(Question, pk=question_id)
    question.deleted_time = timezone.now()
    question.save()
    if request.user == question.post_owner:
        question.is_deleted = True
        question.save()
        return redirect('qa:questionDetailView', pk=question_id)
    else:
        messages.error(request, 'You are not the Post Owner')
        # return JsonResponse({'action':'notPostOwner'})
        return redirect('qa:questionDetailView', pk=question_id)
@login_required
def question_upvote_downvote(request, question_id):
    post = get_object_or_404(Question, pk=question_id)
    likepost = post.qupvote_set.filter(upvote_by_q=request.user).first()
    downVotedPost = post.qdownvote_set.filter(
        downvote_by_q=request.user).first()
    upvote_time_limit = timezone.now() - timedelta(minutes=5)

    # Upvote
    if request.GET.get('submit') == 'like':
        print("upvote")
        if QDownvote.objects.filter(
                downvote_by_q=request.user,
                downvote_question_of=post).exists():
            print(downVotedPost.date)
            print(upvote_time_limit)
           
            QDownvote.objects.filter(
                    downvote_by_q=request.user,
                    downvote_question_of=post).delete()
            m = QUpvote(upvote_by_q=request.user, upvote_question_of=post)
            m.save()
            return redirect('qa:questionDetailView', pk=question_id)
            

        elif QUpvote.objects.filter(upvote_by_q=request.user, upvote_question_of=post).exists():
            print(likepost.date)
            print(upvote_time_limit)
           
            QUpvote.objects.filter(
                    upvote_by_q=request.user,
                    upvote_question_of=post).delete()
            if post.qdownvote_set.all().count() >= 5:
                    post.reversal_monitor = True
                    post.save()
            return redirect('qa:questionDetailView', pk=question_id)
            
        else:
            if request.user == post.post_owner:
                
                return redirect('qa:questionDetailView', pk=question_id)
            else:
                print("else")
                # post.q_reputation += 10
                # post.save()
                created = QUpvote(
                        upvote_by_q=request.user,
                        upvote_question_of=post)
                created.save()
                
                return redirect('qa:questionDetailView', pk=question_id)        
    elif request.GET.get('submit') == 'dislike':
        print("downvote")
        if QUpvote.objects.filter(
                upvote_by_q=request.user,
                upvote_question_of=post).exists():
                m = QDownvote(
                    downvote_by_q=request.user,
                    downvote_question_of=post)
                m.save()
                print("m.save()")
                QUpvote.objects.filter(
                    upvote_by_q=request.user,
                    upvote_question_of=post).delete()
                if post.qdownvote_set.all().count() >= 5:
                    post.reversal_monitor = True
                    post.save()
                return redirect('qa:questionDetailView', pk=question_id)
            
        elif QDownvote.objects.filter(downvote_by_q=request.user, downvote_question_of=post).exists():
          
                QDownvote.objects.filter(
                    downvote_by_q=request.user,
                    downvote_question_of=post).delete()
                
                return redirect('qa:questionDetailView', pk=question_id)
           

        else:
            if request.user == post.post_owner:
                
                return redirect('qa:questionDetailView', pk=question_id)
            else:
                    created = QDownvote(
                        downvote_by_q=request.user,
                        downvote_question_of=post)
                    created.save()
                    return redirect('qa:questionDetailView', pk=question_id)
def AjaxFlagForm(request, question_id):
    data = get_object_or_404(Question, pk=question_id)
    getCreateFlag_object = FlagPost.objects.filter(
        question_forFlag=data).exclude(
        ended=True).first()
    if request.method == 'POST':
        Flag_Form = FlagQuestionForm(data=request.POST)
        print("Hi")
        if Flag_Form.is_valid():
                new_post = Flag_Form.save(commit=False)
                formData = Flag_Form.cleaned_data['actions_Flag_Q']
                getCreateFlag_object = FlagPost.objects.filter(question_forFlag=data).filter(
                         Q(flagged_by=request.user)).exclude(ended=True).all()
                if getCreateFlag_object:
                    cont=FlagPost.objects.filter(question_forFlag=data).count()   
                    if cont>=1:
                       mail_admins(
                        'Hola',
                        'please check the questions'
                       )
                       print("hi hello kic")
                    return JsonResponse({"action": "already flagged"}, status=200)
                else:
                    if formData == "SPAM" or formData == "RUDE_OR_ABUSIVE":
                        getCreateFlag_object = FlagPost.objects.filter(question_forFlag=data).filter(
                            Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True).first()

                        if getCreateFlag_object:
                                new_post.flagged_by = request.user
                                new_post.question_forFlag = data
                                new_post.save()
                                getCreateFlag_object.how_many_votes_on_spamANDRude += 1
                                getCreateFlag_object.save()
                        else:
                            print("Second Statement is Excecuting")
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.how_many_votes_on_spamANDRude += 1
                            new_post.save()
                    elif formData == "VERY_LOW_QUALITY":
                        getCreateFlag_object = FlagPost.objects.filter(
                        question_forFlag=data,
                        actions_Flag_Q="VERY_LOW_QUALITY").exclude(
                        ended=True).first()
                        if getCreateFlag_object:
                            print("Third Statement is Excecuting")
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.save()
                            getCreateFlag_object.save()
                        else:
                            print("Fourth Statement is Excecuting")
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            # new_post.how_many_votes_on_notAnAnswer += 1
                            new_post.save()      
                    elif formData == "IN_NEED_OF_MODERATOR_INTERVATION" or formData == "ABOUT_PROFESSIONAL":
                        getCreateFlag_object = FlagPost.objects.filter(
                            question_forFlag=data).filter(
                            Q(
                                actions_Flag_Q="IN_NEED_OF_MODERATOR_INTERVATION") | Q(
                                actions_Flag_Q="ABOUT_PROFESSIONAL")).exclude(
                            ended=True).first()
                        if getCreateFlag_object:
                            messages.error(
                                request, 'Previous Flag is Waiting for Review')
                        else:
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.save()
                    else:
                        # print("This Statement is Excecuting")
                        getCreateFlag_object = FlagPost.objects.filter(
                            question_forFlag=data).filter(
                            Q(
                                actions_Flag_Q="DUPLICATE") | Q(
                                actions_Flag_Q="OPINION_BASED") | Q(
                                actions_Flag_Q="NEED_MORE_FOCUS") | Q(
                                actions_Flag_Q="NEED_ADDITIONAL_DETAILS") | Q(
                                actions_Flag_Q="NEED_DEBUGGING") | Q(
                                    actions_Flag_Q="NOT_REPRODUCIBLE") | Q(
                                        actions_Flag_Q="BLANTANLTY_OR_CLARITY") | Q(
                                            actions_Flag_Q="ABOUT_GENERAL_COMPUTING_HAR")).exclude(
                                                ended=True).first()
                        if getCreateFlag_object:
                            print("Last Second Statement is Excecuting")
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.save()
                            getCreateFlag_object.how_many_votes_on_others += 1
                            getCreateFlag_object.save()
                        else:
                            print("Last Statement is Excecuting")
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.how_many_votes_on_others += 1
                            new_post.save()
        cont=FlagPost.objects.filter(question_forFlag=data).count()   
        print("Yes me me me") 
        if cont>=1:
            print("Yes")  
        return JsonResponse({"action": "saved"}, status=200)
    return JsonResponse({"error": ""}, status=400)
def answer_upvote_downvote(request, answer_id):
    # que = get_object_or_404(Question, pk=question_id)
    post = get_object_or_404(Answer, pk=answer_id)
    question_URL = request.build_absolute_uri(
        post.questionans.get_absolute_url())
    question_id=post.questionans.id
    getQuestion = Question.objects.get(answer=post)
    if request.GET.get('submit') == 'like':
        if request.user in post.a_vote_downs.all():
            # REMOVE DOWOVOTE AND UPVOTE
            post.a_vote_downs.remove(request.user)
            print("First Statement is Excecuting")
            post.a_vote_ups.add(request.user)
            return redirect('qa:questionDetailView', pk=question_id)
            # Check if user downvoted the post if then delete that downvote
            # reputation (-2) and add new (+10) reputation
            

        elif request.user in post.a_vote_ups.all():
            # REMOVE UPVOTE
            print("Second Statement is Excecuting")
            post.save()
            post.a_vote_ups.remove(request.user)
            
            return redirect('qa:questionDetailView', pk=question_id)
        else:
            # UPVOTE
                # post.date = timezone.now()
                post.save()
                post.a_vote_ups.add(request.user)
                return redirect('qa:questionDetailView', pk=question_id)
    elif request.GET.get('submit') == 'dislike':
        # Remove Upvote and Downvote
        if request.user in post.a_vote_ups.all():
            post.a_vote_ups.remove(request.user)
            post.a_vote_downs.add(request.user)
            return redirect('qa:questionDetailView', pk=question_id)

        elif request.user in post.a_vote_downs.all():
            # Remove DownVote
            post.a_vote_downs.remove(request.user)
            
            return redirect('qa:questionDetailView', pk=question_id)
        else:
                print("Sixth Statement is Excecuting")
                post.a_vote_downs.add(request.user)
                # post.date = timezone.now()
                post.save()
                return redirect('qa:questionDetailView', pk=question_id)
            
    else:
        messages.error(request, 'Something went wrong')
        return redirect('Profile:home')

@login_required
def edit_question(request, question_id):
    post = Question.objects.get(id=question_id)
    post_owner = post.post_owner
    data = get_object_or_404(Question, id=question_id)
    if request.method != 'POST':
        form = UpdateQuestion(request.POST or None,
                              request.FILES or None, instance=post)
    else:
        form = UpdateQuestion(
            instance=post, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save(commit=False)
            post.q_edited_time = timezone.now()
            post.active_date = timezone.now()
            post.q_edited_by = request.user
            request.user.profile.editPostTimeOfUser = timezone.now()
            request.user.profile.save()     
            print(form.errors)
            form.save()
            return redirect('Profile:home')
        else:
            print(form.errors)
            messages.error(request,
                           'Something went wrong!')
    context = {
        'post': post,
        'form': form,
        'post_owner': post_owner}
    return render(request, 'qa/edit_question.html', context)
@login_required
def edit_answer(request, answer_id):
    post = Answer.objects.get(id=answer_id)
    post_owner = post.answer_owner
    data = get_object_or_404(Answer, id=answer_id)
    if request.method == 'POST':
        form = EditAnswerForm(instance=post,
                              data=request.POST,
                              files=request.FILES)
        if form.is_valid():
            form.save(commit=False)
            post.a_edited_time = timezone.now()
            post.active_time = timezone.now()
            post.a_edited_by = request.user
            request.user.profile.editPostTimeOfUser = timezone.now()
            request.user.profile.save() 
            form.save()
            return redirect('Profile:home')
        else:
            messages.error(request, 'Form is Not Valid for some reason')
    else:
        form = EditAnswerForm(request.POST or None,
                              request.FILES or None,
                              instance=post)

    context = {'post': post, 'form': form, 'post_owner': post_owner}
    return render(request, 'qa/edit_answer.html', context)
def undeleteQuestion(request, question_id):
    """
    view to undelete Question
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.post_owner:
        question.is_deleted = False
        question.save()
        return redirect('qa:questionDetailView', pk=question_id)
    else:
        messages.error(request, 'You are not post owner')
        return redirect('qa:questionDetailView', pk=question_id)




    
    
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
def searchQuestion(request):
    context={}
    if request.method=="POST":
      print("Hola")
      searchQ=request.POST.get("searchQ")
      print(searchQ)
      questions=Question.objects.filter(title__icontains=searchQ).all()
      return render(request,'qa/searchQuestions_list.html',{'questions':questions})
    return render(request,'qa/searchQuestions_list.html',context)