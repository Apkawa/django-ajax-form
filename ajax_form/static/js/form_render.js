
function JSONForm(form_data, values) {
    if (typeof(form_data) == 'string') {
        this.form_data = JSON.parse(form_data)
    } else {
        this.form_data = form_data
    }
    this.values = values || this.get_values_fields()
}

JSONForm.prototype.render = function () {
    var fields = this.form_data['fields'];
    var result = "";
    for (f_name in fields) {
        result = result + this.render_field(f_name, fields[f_name], this.values[f_name]);
    }
    return result
}

JSONForm.prototype.as_ul = function () {
    var fields = this.form_data['fields'];
    var result = "";
    if ('__all__' in this.form_data['errors']) {
        result = result + this.form_data['errors']['__all__'];
    }
    for (f_name in fields) {
        var errors = this.render_error(this.form_data['errors'][f_name]);
        result = result
                    + '<li>'
                    + this.render_field(f_name, fields[f_name], this.values[f_name])
                    +  '</li>'
                    + errors
    }
    return result
}


JSONForm.prototype.get_values_fields = function () {
    var values = {}
    var fields = this.form_data['fields'];
    for (f_name in fields) {
        values[f_name] = this.form_data['fields'][f_name]['value'];
    }
    return values
}

JSONForm.prototype.render_error = function(errors) {
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
    var with_label = with_label || true;
    if (! ('id' in field)) {
        field['id'] = 'id_' + field_name;
    }
    label = '';
    if (with_label) {
        label = this.build_label(field['id'], field['label'] || field_name)
    }
    field['name'] = field_name;

    if (type in {'textarea':1, 'hidden':1, 'text':1, 'checkbox':1}) {

        rendered_field = this.render_input_field(field, value, type);
        if (type == 'checkbox') {
            rendered_field = rendered_field + label;
        } else {
            rendered_field = label + rendered_field;
        }
        return rendered_field;
    }
    if (type == 'select') {
        return label + this.render_select_field(field, value, type);
    }
    return this.render_input_field(field, value, 'text');
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
    var result = '<select '+ this.build_attrs(attrs) + '>';
    var choices = field['choices'];
    for (choice in choices) {
        option = {value: choices[choice][0]}
        if (value == choices[choice][0]) {
            option['selected'] = 'selected';
        }
        result = result + '<option '+ this.build_attrs(option) + '>' + choices[choice][1] + '</option>';
    }
    result = result + '</select>';
    return result;
}
