

def handle_err_page(request, templates, status, msg):
    templates.TemplateResponse(
        request=request,
        name="/error/4xx.html" if status < 500 else "/error/5xx.html",
        context={
            "status_code": status,
            "msg": msg
        }
    )




