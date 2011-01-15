import unittest

from formencode import Schema
from formencode import validators

from pyramid import testing
from pyramid.config import Configurator


class SimpleSchema(Schema):

    name = validators.NotEmpty()


class SimpleObj(object):

    def __init__(self, name=None):
        self.name = name


class TestForm(unittest.TestCase):
    
    def test_is_error(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
        self.assert_('name' in form.errors)

    def test_errors_for(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
        self.assert_('name' in form.errors)

        self.assert_(form.errors_for('name') == ['Missing value'])


    def test_validate_twice(self):
        
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

        request.POST = {'name' : 'ok again'}

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

    def test_validate_good_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST = {'name' : 'ok'}

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assert_(form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.data['name'] == 'ok')

    def test_validate_bad_input_with_validators(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, 
                    validators=dict(name=validators.NotEmpty()))

        self.assert_(not form.validate())
        self.assert_(form.is_validated)
        self.assert_(form.is_error('name'))

        self.assert_(form.errors_for('name') == ['Please enter a value'])

    def test_is_validated_on_post(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        self.assert_(form.is_validated)
 
    def test_bind(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()
        obj = form.bind(SimpleObj())
        self.assert_(obj.name == 'test')
        
    def test_bind_not_validated_yet(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        self.assertRaises(RuntimeError, form.bind, SimpleObj())
 
    def test_bind_with_errors(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = ''

        form = Form(request, SimpleSchema)
        self.assert_(not form.validate())
        self.assertRaises(RuntimeError, form.bind, SimpleObj())

    def test_bind_with_exclude(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()
        obj = form.bind(SimpleObj(), exclude=["name"])
        self.assert_(obj.name == None)
 
    def test_bind_with_include(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()
        obj = form.bind(SimpleObj(), include=['foo'])
        self.assert_(obj.name == None)
 
    def test_initialize_with_obj(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, obj=SimpleObj(name='test'))

        self.assert_(form.data['name'] == 'test')

    def test_initialize_with_defaults(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={'name' : 'test'})

        self.assert_(form.data['name'] == 'test')

    def test_initialize_with_obj_and_defaults(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, 
                    obj=SimpleObj(name='test1'),
                    defaults={'name' : 'test2'})

        self.assert_(form.data['name'] == 'test1')

    def test_variable_decode(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.POST['name'] = 'test'
        request.method = "POST"
        
        form = Form(request, SimpleSchema,
                    variable_decode=True)

        self.assert_(form.validate())
        self.assert_(form.data['name'] == 'test')

    def test_validate_from_GET(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        request.method = "GET"
        request.GET['name'] = 'test'

        form = Form(request, SimpleSchema, method="GET")

        self.assert_(form.validate())
        self.assert_(form.is_validated)
 
    def test_htmlfill(self):
        from pyramid_simpleform import Form

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, 
                    defaults={"name" : "testing"})

        html = """
        <form method="POST" action=".">
            <input type="text" name="name">
        </form>
        """

        html = form.htmlfill(html)
        self.assert_('value="testing"' in html)


class TestFormRenderer(unittest.TestCase):
    
    def test_begin_form(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.begin(url="/"),
                     '<form action="/" method="post">')

    def test_end_form(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.end() == "</form>")

    def test_csrf(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.csrf() == \
                '<input name="_csrf" type="hidden" value="csrft" />')
 
    def test_csrf_token(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.csrf_token() == \
                '<div style="display:none;"><input name="_csrf" '
                'type="hidden" value="csrft" /></div>')
 
    def test_text(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assert_(renderer.text("name") == \
                '<input name="name" type="text" value="Fred" />')

    def test_textarea(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assert_(renderer.textarea("name") == \
                '<textarea name="name">Fred</textarea>')
 
    def test_hidden(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)

        self.assert_(renderer.hidden("name") == \
                '<input name="name" type="hidden" value="Fred" />')
        
    def test_select(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : "Fred"})
        renderer = FormRenderer(form)
        
        options = [
            ("Fred", "Fred"),
            ("Barney", "Barney"),
            ("Wilma", "Wilma"),
            ("Betty", "Betty"),
        ]   

        self.assert_(renderer.select("name", options) == \
            """<select name="name">
<option selected="selected" value="Fred">Fred</option>
<option value="Barney">Barney</option>
<option value="Wilma">Wilma</option>
<option value="Betty">Betty</option>
</select>""")
 
    def test_file(self):
  
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.file('file') == \
                   '<input name="file" type="file" />')

    def test_password(self):
  
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.password('password') == \
                   '<input name="password" type="password" />')


    def test_radio(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : 'Fred'})
        renderer = FormRenderer(form)
        
        self.assert_(renderer.radio("name", value="Fred") == \
                     '<input checked="checked" id="name_fred" name="name" '
                     'type="radio" value="Fred" />')
        
        self.assert_(renderer.radio("name", value="Barney") == \
                     '<input id="name_barney" name="name" '
                     'type="radio" value="Barney" />')

    def test_submit(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)

        self.assert_(renderer.submit("submit", "Submit") == \
                     '<input name="submit" type="submit" value="Submit" />')

    def test_checkbox(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema, defaults={"name" : True})
        renderer = FormRenderer(form)
        
        self.assert_(renderer.checkbox("name") == \
                     '<input checked="checked" name="name" type="checkbox" '
                     'value="1" />')

    def test_is_error(self):
        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))

        renderer = FormRenderer(form)
        self.assert_(renderer.is_error('name'))

    def test_errors_for(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)

        self.assert_(not(form.validate()))
        renderer = FormRenderer(form)

        self.assert_(renderer.errors_for('name') == ['Missing value'])

    def test_errorlist(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist() == \
                     '<ul class="error"><li>Missing value</li></ul>')
     

    def test_errorlist_with_no_errors(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"
        request.POST['name'] = 'test'

        form = Form(request, SimpleSchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist() == '')
 
    def test_errorlist_with_field(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        request.method = "POST"

        form = Form(request, SimpleSchema)
        form.validate()

        renderer = FormRenderer(form)

        self.assert_(renderer.errorlist('name') == \
                     '<ul class="error"><li>Missing value</li></ul>')
 
    def test_label(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.label("name") == \
                   '<label for="name">Name</label>') 

    def test_label_using_field_name(self):

        from pyramid_simpleform import Form
        from pyramid_simpleform.renderers import FormRenderer

        request = testing.DummyRequest()
        form = Form(request, SimpleSchema)
        renderer = FormRenderer(form)
       
        self.assert_(renderer.label("name", "Your name") == \
                   '<label for="name">Your name</label>') 


