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
from django.db.models import Case, When
from openpyxl import load_workbook
import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
# Create your views here.

#cosine similarity
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
df=pd.read_excel('C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/qa/cosine_similarity_data.xlsx')


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

    
    answers_of_questions = sorted(data.answer_set.all(), key = lambda x: x.countAllTheVotes,reverse=True) 
     
    #Answer.objects.filter(pk__in=ratings_list)
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
            print("iM HERE")
            gettingBody = form.cleaned_data['body']
            new_post = form.save(commit=False)
            new_post.answer_owner = request.user
            new_post.questionans = data
            data.active_date = timezone.now()
            data.save()
            new_post.save()
            return render(request, 'qa/questions')
    else:
        form=AnswerForm()    
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
        my_conn = sqlite3.connect("C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/db.sqlite3")
        try:
          query="SELECT * FROM qa_Question" # query to collect record 
          df = pd.read_sql(query,my_conn,index_col='id') # create DataFrame
          print(df.head()) # Print top 5 rows as sample
          df.to_excel('C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/qa/Question-2023-02-05.xlsx')  # create the excel file 
        except SQLAlchemyError as e:
          error = str(e.__dict__['orig'])
          print(error)
        else:
          print("DataFrame created successfully..")
          my_conn.close()
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
                    my_conn = sqlite3.connect("C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/db.sqlite3")
                    cursor_obj = my_conn.cursor() 
                    cursor_obj.execute("SELECT * FROM auth_user")
                    l=cursor_obj.fetchall()
                    my_conn.close()
                    l=(int)(0.1)*len(l)
                    if cont>=l:
                       mail_admins(
                        'Campus Connect',
                        'Please check the question with id '+str(question_id)+' and delete the question'
                       )
                    return redirect("Profile:home")
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
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.save()
                            getCreateFlag_object.save()
                        else:
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
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.save()
                            getCreateFlag_object.how_many_votes_on_others += 1
                            getCreateFlag_object.save()
                        else:
                            new_post.flagged_by = request.user
                            new_post.question_forFlag = data
                            new_post.how_many_votes_on_others += 1
                            new_post.save()
                cont=FlagPost.objects.filter(question_forFlag=data).count()   
                my_conn = sqlite3.connect("C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/db.sqlite3")
                cursor_obj = my_conn.cursor() 
                cursor_obj.execute("SELECT * FROM auth_user")
                l=cursor_obj.fetchall()
                my_conn.close()
                l=(int)(0.1)*len(l)
                if cont>=l:
                  mail_admins(
                        'Campus Connect',
                        'Please check the question with id '+str(question_id)+' and delete the question'
                       )  
        return redirect("Profile:home")
    return redirect("Profile:error_Page")
def answer_upvote_downvote(request, answer_id):
    # que = get_object_or_404(Question, pk=question_id)
    post = get_object_or_404(Answer, pk=answer_id)
    question_URL = request.build_absolute_uri(
        post.questionans.get_absolute_url())
    question_id=post.questionans.id
    getQuestion = Question.objects.get(answer=post)
    if request.GET.get('submit') == 'like':
        if request.user in post.a_vote_downs.all():
            post.a_vote_downs.remove(request.user)
            print("First Statement is Excecuting")
            post.a_vote_ups.add(request.user)
            return redirect('qa:questionDetailView', pk=question_id)

        elif request.user in post.a_vote_ups.all():
            print("Second Statement is Excecuting")
            post.save()
            post.a_vote_ups.remove(request.user)
            
            return redirect('qa:questionDetailView', pk=question_id)
        else:
                post.save()
                post.a_vote_ups.add(request.user)
                return redirect('qa:questionDetailView', pk=question_id)
    elif request.GET.get('submit') == 'dislike':
        if request.user in post.a_vote_ups.all():
            post.a_vote_ups.remove(request.user)
            post.a_vote_downs.add(request.user)
            return redirect('qa:questionDetailView', pk=question_id)

        elif request.user in post.a_vote_downs.all():
            post.a_vote_downs.remove(request.user)
            
            return redirect('qa:questionDetailView', pk=question_id)
        else:
                print("Sixth Statement is Excecuting")
                post.a_vote_downs.add(request.user)
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
                            my_conn = sqlite3.connect("C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/db.sqlite3")
                            try:
                              query="SELECT * FROM qa_Question" # query to collect record 
                              df = pd.read_sql(query,my_conn,index_col='id') # create DataFrame
                              print(df.head()) # Print top 5 rows as sample
                              df.to_excel('C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/qa/Question-2023-02-05.xlsx')  # create the excel file 
                            except SQLAlchemyError as e:
                              error = str(e.__dict__['orig'])
                              print(error)
                            else:
                              print("DataFrame created successfully..")
                              my_conn.close()
                            return redirect('qa:questions')           
    else:
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


# def calcTFIDF():
#     print("hello")
#     df=pd.read_csv('C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/qa/Question-2023-02-05.csv')
#     # print(df)
#     # Use a CountVectorizer to learn the terms and term frequencies across all of the documents (carols) 
#     cv = CountVectorizer(stop_words='english')
#     doc_term_matrix = cv.fit_transform(df['title'])
#     word_counts = pd.DataFrame(doc_term_matrix.toarray(), index=df["body"], columns=cv.get_feature_names_out())
#     word_counts.sum().sort_values(ascending=False)
#     idfs = TfidfTransformer() 
#     idfs.fit(doc_term_matrix)
#     idfs_df = pd.DataFrame(idfs.idf_, index=cv.get_feature_names_out(), columns=["idfs"]) 
 
#     # Sort ascending and display
#     # High IDF (1/DF) terms are less frequent across all documents; low IDF terms are more frequent 
#     idfs_df.sort_values(by=['idfs'], ascending=False)
#     # We have the term frequencies and inverse document frequencies - now calculate the TF-IDF scores
#     tf_idfs = idfs.transform(doc_term_matrix)
#     doc = 0
#     col = "tf-idf for doc {}".format(doc)
#     tf_idf_doc = pd.DataFrame(tf_idfs[doc].T.todense(), index=cv.get_feature_names_out(), columns=[col])
#     tf_idf_doc.sort_values(by=[col], ascending=False)
    
#     tf_idf_all_docs = pd.DataFrame(tf_idfs.T.todense(), index=cv.get_feature_names_out())
#     tf_idf_all_docs_nicer = pd.DataFrame(np.transpose(tf_idfs.T.toarray()), index=df["body"], columns=cv.get_feature_names_out())
#     print(tf_idf_doc)
#     return tf_idfs, cv

# def searchQuery(query):
#     tf_idfs,cv=calcTFIDF()
#     idx=[]
#     query_term_matrix = cv.transform([query])
#     print(query_term_matrix)
#     results = cosine_similarity(tf_idfs, query_term_matrix)
#     results = results.reshape((-1,))
#     print("Search results for: '{}'".format(query))
#     for i in results.argsort()[:-11:-1]:
#         if results[i] > 0:
#             print("Body {} {}. {} {}%".format(i, df.iloc[i,0],df.iloc[i,2], round(100*results[i])))
#             idx.append(df.iloc[i,0])
#             # print(df.iloc[i,0],df.iloc[i,2])
#     return idx

def searchQuestion(request):
    context={}
    if request.method=="POST":
      print("Hola")
      searchQ=request.POST.get("searchQ")
      df=pd.read_excel('C:/Users/dell/Dropbox/PC/Desktop/FYP/Campus-Connect/CC/qa/Question-2023-02-05.xlsx')
      cv = CountVectorizer(stop_words='english')
      doc_term_matrix = cv.fit_transform(df['title'])
      doc_term_matrix.shape
      cv.get_feature_names_out()
      word_counts = pd.DataFrame(doc_term_matrix.toarray(), index=df["body"], columns=cv.get_feature_names_out())
      word_counts.sum().sort_values(ascending=False)
      print("word counts for job")
      print(word_counts[["career", "job"]])
      idfs = TfidfTransformer() 
      idfs.fit(doc_term_matrix)
      idfs_df = pd.DataFrame(idfs.idf_, index=cv.get_feature_names_out(), columns=["idfs"]) 
 
      # Sort ascending and display
      # High IDF (1/DF) terms are less frequent across all documents; low IDF terms are more frequent 
      idfs_df.sort_values(by=['idfs'], ascending=False)
      # We have the term frequencies and inverse document frequencies - now calculate the TF-IDF scores
      tf_idfs = idfs.transform(doc_term_matrix)
      doc = 0
      col = "tf-idf for doc {}".format(doc)
      tf_idf_doc = pd.DataFrame(tf_idfs[doc].T.todense(), index=cv.get_feature_names_out(), columns=[col])
      tf_idf_doc.sort_values(by=[col], ascending=False)
       # Create a data frame to view all of the TF-IDF scores
      tf_idf_all_docs = pd.DataFrame(tf_idfs.T.todense(), index=cv.get_feature_names_out())
      tf_idf_all_docs
      tf_idf_all_docs_nicer = pd.DataFrame(np.transpose(tf_idfs.T.toarray()), index=df["body"], columns=cv.get_feature_names_out())
      tf_idf_all_docs_nicer

      
      # Calculate term frequencies for the query using terms found across all of the documents
      query_term_matrix = cv.transform([searchQ])
      print(query_term_matrix)
      query_counts = pd.DataFrame(query_term_matrix.toarray(), columns=cv.get_feature_names_out())
      splits=searchQ.split(" ")
      results = cosine_similarity(tf_idfs, query_term_matrix)
      results = results.reshape((-1,))
      idx2=[]
      for i in results.argsort()[:-11:-1]:
        if results[i] > 0:
          idx2.append((df.iloc[i,0],round(100*results[i])))
      pk_list = [idx for idx,rating in idx2]
      preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(pk_list)])  
      queryset = Question.objects.filter(pk__in=pk_list).order_by(preserved)
      print(queryset)
      return render(request,'qa/searchQuestions_list.html',{'questions':queryset})
    return render(request,'qa/searchQuestions_list.html',context)