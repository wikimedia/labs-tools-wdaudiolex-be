from datetime import datetime, timezone

from service import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pref_langs = db.Column(db.String(255), nullable=False, default="en")
    temp_token = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"User(username={self.username}, pref_langs={self.pref_langs})"


class ContributionModel(db.Model):
    __tablename__ = "contributions"

    id = db.Column(db.Integer, primary_key=True, index=True)
    wd_item = db.Column(db.String(150))
    form_id = db.Column(db.String(150))
    username = db.Column(db.String(80), index=True)
    lang_code = db.Column(db.String(25), index=True)
    audio_filename = db.Column(db.String(255), index=True)
    variety_qid = db.Column(db.String(32), nullable=True)
    edit_type = db.Column(db.String(150), default="pronunciation_audio")
    data = db.Column(db.Text)
    revision_id = db.Column(db.String(50), nullable=True)
    date = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return "Contribution({}, {}, {}, {})".format(
            self.wd_item,
            self.username,
            self.lang_code,
            self.date,
        )
