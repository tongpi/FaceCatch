from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import DataRequired


class UploadForm(FlaskForm):
    """
    上传需要比对的图片
    """
    file = FileField("上传图片", validators=[DataRequired()])
    submit = SubmitField("搜索")