
function JSONForm(form_data, values) {
    if (typeof(form_data) == 'string') {
        this.form_data = JSON.parse(form_data)
    } else {
        this.form_data = form_data
    }
}

JSONForm.prototype.is_in = function (value, sequence) {
    for (s in sequence) {
        if (value == sequence[s]) {
            return true;
        }
    }
    return false;
}

JSONForm.prototype.value_or_default = function (value, default_value) {
    if (typeof(value) == 'undefined') {
        return default_value;
    }
    return value;
}

JSONForm.prototype.clone = function (obj) {
    if (null == obj || "object" != typeof obj) return obj;
    var copy = obj.constructor();
    for (var attr in obj) {
        if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
    }
    return copy;
}

JSONForm.prototype.render = function () {
    var form_data = this.form_data
    if (typeof(form_data) == 'object') {
        return this.render_form(form_data)
    } else if (typeof(form_data) == 'array' ) {
        return this.render_formset(form_data)
    }
}

JSONForm.prototype.render_formset = function (formset_data, form_renderer) {
    var formset_data = formset_data || this.form_data
    var form_renderer = form_renderer || this.as_ul
    var result = '';
    for (i in formset_data) {
        result = result + form_renderer.call(this, formset_data[i]);
    }
    return result

}

JSONForm.prototype.render_form = function (form_data, form_renderer) {
    var form_data = form_data || this.form_data
    var form_renderer = form_renderer || this.as_ul
    return form_renderer.call(this, form_data)
}


JSONForm.prototype.as_ul = function (form_data) {
    var fields = form_data['fields'];
    var values = this.get_values_fields(form_data)
    var result = "";
    if ('__all__' in form_data['errors']) {
        result = result + form_data['errors']['__all__'];
    }
    for (f_name in fields) {
        var field = fields[f_name]
        if (field['type'] == 'hidden') {
            result = result + this.render_field(f_name, field, values[f_name], false)
        } else {
            var errors = this.render_error(form_data['errors'][f_name]);

            result = result
                        + '<li>'
                        + this.render_field(f_name, field, values[f_name])
                        +  '</li>'
                        + errors
        }
    }
    return result
}


JSONForm.prototype.get_values_fields = function (form_data) {
    var values = {}
    var fields = form_data['fields'];
    for (f_name in fields) {
        values[f_name] = form_data['fields'][f_name]['value'];
    }
    return values
}

JSONForm.prototype.render_error = function (errors) {
    if (!errors) {
        return '';
    }
    var result = '<ul class="errorlist">';
    for (i in errors) {
        result = result + '<li>' + errors[i] + '</li>';
    }
    result = result + '</ul>';
    return result

}


JSONForm.prototype.render_field = function (field_name, field, value, with_label) {
    var type = field['type'];
    var with_label = this.value_or_default(with_label, true);
    if (! ('id' in field)) {
        field['id'] = 'id_' + field_name;
    }
    label = '';
    if (with_label) {
        label = this.build_label(field['id_for_label'] || field['id'], field['label'] || field_name)
    }
    field['name'] = field['html_name'];

    if (type in {'textarea':1, 'hidden':1, 'text':1, 'checkbox':1}) {

        rendered_field = this.render_input_field(field, value, type);
        if (type == 'checkbox') {
            rendered_field = rendered_field + label;
        } else {
            rendered_field = label + rendered_field;
        }
        return rendered_field;
    }
    if (type in {'select':1, 'selectmultiple':1}) {
        return label + this.render_select_field(field, value, type);
    }
    if (type == 'radio') {
        return label + this.render_radio_field(field, value, type);
    }
    return label + this.render_input_field(field, value, 'text');
}

JSONForm.prototype.build_attrs = function (attrs) {
    var builded_attrs = '';
    for (attr_name in attrs){
        builded_attrs = builded_attrs + attr_name + '="' + attrs[attr_name] + '" ';
    }
    return builded_attrs

}

JSONForm.prototype.build_label = function(field_id, text) {
    return "<label " + this.build_attrs({'for': field_id}) + '>' + text + '</label>';
}

JSONForm.prototype.render_input_field = function (field, value, type) {
    var attrs = field['widget_attrs'];
    attrs['type'] = type || field['type'];
    if (type == 'checkbox') {
        if (value) {
            attrs['checked'] = 'checked';
        }
    } else {
        attrs['value'] = value || '';
    }
    attrs['name'] = field['name'];
    attrs['id'] = field['id'];
    var result = '<input '+ this.build_attrs(attrs) + '/>';
    return result
}

JSONForm.prototype.render_select_field = function (field, value, type) {
    var attrs = field['widget_attrs'];
    attrs['name'] = field['name'];
    attrs['id'] = field['id'];
    if (type == 'selectmultiple') {
        attrs['multiple'] = 'multiple';
    }
    if (this.is_in(typeof(value), ['undefined', 'null'])) {
        value = []
    } else if (typeof(value) == 'string') {
        value = [value]
    }
    var result = '<select '+ this.build_attrs(attrs) + '>';
    var choices = field['choices'];
    for (choice in choices) {
        option = {value: choices[choice][0]}
        if (this.is_in(choices[choice][0], value)) {
            option['selected'] = 'selected';
        }
        result = result + '<option '+ this.build_attrs(option) + '>' + choices[choice][1] + '</option>';
    }
    result = result + '</select>';
    return result;
}

JSONForm.prototype.render_radio_field = function (field, value, type) {
    var attrs = field['widget_attrs'];
    attrs['name'] = field['name'];
    attrs['id'] = field['id'];

    var result = '<ul>'
    var choices = field['choices'];
    for (i=0; i < choices.length; i++) {
        input_field = {'name': field['name'], 'id': field['id'] + '_' + i,
            'widget_attrs': this.clone(attrs)}
        if (value == choices[i][0]) {
            input_field['widget_attrs']['checked'] = 'checked';
        }
        result = result
                + '<li>'
                + this.render_input_field(input_field, choices[i][0], 'radio')
                + this.build_label(input_field['id'], choices[i][1])
                + '</li>';
    }
    result = result + '</ul>';
    return result;
}
