from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import DataRequired


class AddForm(FlaskForm):
    """
    添加人员信息
    """
    file = FileField("上传照片", validators=[DataRequired()])
    name = StringField("姓名")
    id_card = StringField("证件号")
    description = StringField("描述")
    submit = SubmitField("提交")


class UpdateForm(FlaskForm):
    """
    更新人员信息
    """
    file = FileField("上传照片", default='')
    name = StringField("姓名")
    id_card = StringField("证件号")
    description = StringField("描述")
    submit = SubmitField("提交修改")


class BatchAddForm(FlaskForm):
    """
    批量添加人员信息
    """
    file = FileField("上传ZIP文件", validators=[DataRequired()])
    submit = SubmitField("提交")
