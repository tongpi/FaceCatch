from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, SelectField
from wtforms.validators import DataRequired
from facecatch.utils import get_models


class UploadForm(FlaskForm):
    """
    上传需要比对的图片
    """
    file = FileField("上传图片", validators=[DataRequired()])
    submit = SubmitField("搜索")
    select = SelectField('选择识别模型', validators=[DataRequired()], choices=get_models())
