
def user_data(request):
    return{
       'globaladmin' : request.session.get('globaladmin', None),
       'globalusername':request.session.get('globalusername', None),
       'globaluser_admin':request.session.get('globaluser_admin',None)
    }