from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout


class LogController(object):


    def logout_view(self, request):
        logout(self, request)
        return redirect(self.login_view)

    def login_view(self, request):
        message='';
        if request.method == 'POST':
            username = request.POST['InputUser']
            password = request.POST['InputPassword']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect(self.menu_view)
            else:
                message = 'Usuario o Contrasenia Incorrecto.'

        context = {'message': message}
        return render(request, 'cawas/login.html', context)




    def menu_view (self, request):
        if not request.user.is_authenticated:
            return redirect(self.login_view)

        #<Definir Variables>
        idassetstype = 0
        message = 'Hay 0 contenidos sin publicar.'
        contentypes = (
            (1, "MOVIE"),
            (2, "BLOQUES"),
            (3, "CHICAS"),
            (4, "CATEGORIAS"),
            (5, "CAPITULOS"),
            (6, "SLIDERS")
        )

        assetstypes = (
            (1, "Movies"),
            (2, "Serie"),
            (3, "Bloques"),
            (4, "Chicas"),
            (6, "Capitulos"),
            (7, "Sliders")
        )
        # </Definir Variables>

        title = 'Menu Principal'
        context = {'title': title, 'assetstypes':assetstypes, 'message': message ,  'idassetstype': idassetstype}
        return render(request, 'cawas/menu.html', context)