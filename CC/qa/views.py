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
    answers_of_questions = data.answer_set.all()
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

            if downVotedPost.date > upvote_time_limit:
                QDownvote.objects.filter(
                    downvote_by_q=request.user,
                    downvote_question_of=post).delete()
                m = QUpvote(upvote_by_q=request.user, upvote_question_of=post)
                m.save()
                return JsonResponse({'action': 'undislike_and_like'})
            else:
                return JsonResponse({'action': 'voteError'})

        elif QUpvote.objects.filter(upvote_by_q=request.user, upvote_question_of=post).exists():
            if likepost.date > upvote_time_limit :
                QUpvote.objects.filter(
                    upvote_by_q=request.user,
                    upvote_question_of=post).delete()
                if post.qdownvote_set.all().count() >= 5:
                    post.reversal_monitor = True
                    post.save()
                return JsonResponse({'action': 'unlike'})
            else:
                return JsonResponse({'action': 'voteError'})
        else:
            if request.user == post.post_owner:
                print("Hola mamamiyaa   adios")
                return JsonResponse({'action': 'cannotLikeOwnPost'})
            else:
                print("else")
                # post.q_reputation += 10
                # post.save()
                created = QUpvote(
                        upvote_by_q=request.user,
                        upvote_question_of=post)
                created.save()
                print("Hola mamamiyaa")
                return JsonResponse({'action': 'like_only'})        
    elif request.GET.get('submit') == 'dislike':
        print("downvote")
        if QUpvote.objects.filter(
                upvote_by_q=request.user,
                upvote_question_of=post).exists():
            if likepost.date > upvote_time_limit :
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
                return JsonResponse({'action': 'unlike_and_dislike'})
            else:
                return JsonResponse({'action': 'voteError'})
        elif QDownvote.objects.filter(downvote_by_q=request.user, downvote_question_of=post).exists():
            if downVotedPost.date > upvote_time_limit :
                QDownvote.objects.filter(
                    downvote_by_q=request.user,
                    downvote_question_of=post).delete()
                
                return JsonResponse({'action': 'undislike'})
            else:
                return JsonResponse({'action': 'voteError'})

        else:
            if request.user == post.post_owner:
                
                return JsonResponse({'action': 'cannotLikeOwnPost'})
            else:
                    created = QDownvote(
                        downvote_by_q=request.user,
                        downvote_question_of=post)
                    created.save()
                    return JsonResponse({'action': 'dislike_only'})

def AjaxFlagForm(request, question_id):
    """
    Ajax form to submit Question's Flag
    """
    data = get_object_or_404(Question, pk=question_id)

    getCreateFlag_object = FlagPost.objects.filter(
        question_forFlag=data).exclude(
        ended=True).first()

    if request.method == 'POST':
        Flag_Form = FlagQuestionForm(data=request.POST)
        if Flag_Form.is_valid():
            new_post = Flag_Form.save(commit=False)
            formData = Flag_Form.cleaned_data['actions_Flag_Q']

            if request.user.profile.flag_posts:
                if formData == "SPAM" or formData == "RUDE_OR_ABUSIVE":
                    getCreateFlag_object = FlagPost.objects.filter(question_forFlag=data).filter(
                        Q(actions_Flag_Q="SPAM") | Q(actions_Flag_Q="RUDE_OR_ABUSIVE")).exclude(ended=True).first()
                    if getCreateFlag_object:
                        print("First Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_spamANDRude += 1
                        getCreateFlag_object.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE",
                            questionIf_TagOf_Q=data)
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        print("Second Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.how_many_votes_on_spamANDRude += 1
                        new_post.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        # createReviewInstance,created = ReviewFlagPost.objects.get_or_create(flag_question_to_view=data)
                        # createReviewInstance.flag_reviewed_by.add(request.user)
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

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
                        # getCreateFlag_object.how_many_votes_on_notAnAnswer += 1
                        getCreateFlag_object.save()
                        # createReviewInstance,created = ReviewFlagPost.objects.get_or_create(flag_question_to_view=data, flag_of=new_post)
                        # createReviewInstance.flag_reviewed_by.add(request.user)
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                            suggested_by=request.user, low_is=data, why_low_quality="Very Low Quality", suggested_through="User")
                        createLowQualityReviewInstance = ReviewLowQualityPosts.objects.get_or_create(
                            review_of=create_Low_Quality_Post_Instance, is_question=data)
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        print("Fourth Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        # new_post.how_many_votes_on_notAnAnswer += 1
                        new_post.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        create_Low_Quality_Post_Instance, cre = LowQualityPostsCheck.objects.get_or_create(
                            suggested_by=request.user, low_is=data, why_low_quality="Very Low Quality", suggested_through="User")
                        ReviewLowQualityPosts.objects.get_or_create(
                            review_of=create_Low_Quality_Post_Instance, is_question=data)
                        # createReviewInstance,created = ReviewFlagPost.objects.get_or_create(flag_question_to_view=data, flag_of=new_post)
                        # createReviewInstance.flag_reviewed_by.add(request.user)
                        # return redirect('qa:questionDetailView', pk=data.id)

                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

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
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data, flag_of=new_post)
                        createReviewInstance.flag_reviewed_by = request.user
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                # elif formData == "DUPLICATE" or formData == "OPINION_BASED"
                # or formData == "NEED_MORE_FOCUS" or formData ==
                # "NEED_ADDITIONAL_DETAILS" or formData == "NEED_DEBUGGING" or
                # formData == "NOT_REPRODUCIBLE" or formData ==
                # "BLANTANLTY_OR_CLARITY" or formData ==
                # "SEEKING_RECCOMENDATIONS" or:
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

                        createLowInstance, cre = CloseQuestionVotes.objects.get_or_create(
                            user=request.user, question_to_closing=data, why_closing="Duplicate", ended=False)
                        # getInstanceNow = CloseQuestionVotes.objects.filter(id=createLowInstance)
                        print(createLowInstance.id)
                        createInstance, created = ReviewCloseVotes.objects.get_or_create(
                            question_to_closed=data)
                        createInstance.review_of = createLowInstance
                        createInstance.save()

                        new_post.save()
                        getCreateFlag_object.how_many_votes_on_others += 1
                        getCreateFlag_object.save()
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data)
                        createReviewInstance.flag_reviewed_by = request.user
                        # createInstance.review_of = createLowInstance
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                    else:
                        print("Last Statement is Excecuting")
                        new_post.flagged_by = request.user
                        new_post.question_forFlag = data
                        new_post.how_many_votes_on_others += 1
                        new_post.save()
                        createReviewInstance, created = ReviewFlagPost.objects.get_or_create(
                            flag_question_to_view=data)
                        createReviewInstance.flag_reviewed_by = request.user

                        create_Low_Quality_Post_Instance, cre = CloseQuestionVotes.objects.get_or_create(
                            user=request.user, question_to_closing=data, why_closing="Duplicate", ended=False)
                        createInstance, created = ReviewCloseVotes.objects.get_or_create(
                            question_to_closed=data)
                        TagBadge.objects.get_or_create(
                            awarded_to_user=request.user,
                            badge_type="BRONZE",
                            tag_name="Citizen Patrol",
                            bade_position="BADGE")
                        createInstance.review_of = create_Low_Quality_Post_Instance
                        createInstance.save()
                        # return redirect('qa:questionDetailView', pk=data.id)
                        PrivRepNotification.objects.get_or_create(
                            for_user=request.user,
                            url="#",
                            type_of_PrivNotify="BADGE_EARNED",
                            for_if="Citizen Patrol",
                            description="First flagged post"
                        )

                # elif formData == "ABOUT_GENERAL_COMPUTING_HAR" or formData == "ABOUT_PROFESSIONAL":
                #         new_post.flagged_by = request.user
                #         new_post.question_forFlag = data
                #         new_post.save()

                # else:
                    # messages.error(request, "Response is Out Of Network")

                # new_post.user = request.user
                # new_post.question_forFlag = data
                # new_post.save()
                # return redirect('qa:questionDetailView', pk=data.id,)  #
                # slug=slug)
                ser_instance = serializers.serialize('json', [
                    new_post,
                ])
                # send to client side.
                return JsonResponse({"action": "saved"}, status=200)
            else:
                return JsonResponse({'action': "lackOfPrivelege"})
            # else:
                # return JsonResponse({"action": "cannotCreate"}, status=200)
        else:
            # some form errors occured.
            return JsonResponse({"error": Flag_Form.errors}, status=400)

    # errors occured (if occured)
    return JsonResponse({"error": ""}, status=400)
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