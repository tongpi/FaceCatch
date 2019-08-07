from wtforms import FileField, SubmitField, StringField, Form
from wtforms.validators import DataRequired


class UploadForm(Form):
    """
    上传需要比对的图片
    """
    file = FileField("上传图片", validators=[DataRequired()])
    job_id = StringField("JOB_ID", validators=[DataRequired()])
    submit = SubmitField("搜索")


class UploadSoundForm(Form):
    """
    上传需要预测的声音文件
    """
    file = FileField("上传声音文件", validators=[DataRequired()])
    job_id = StringField("JOB_ID", validators=[DataRequired()])
    submit = SubmitField("搜索")
