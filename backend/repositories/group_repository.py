from sqlalchemy.orm import Session
from sqlalchemy import func
from models.models import Group, User, Membership
from features.groups.schemas.group_schema import GroupCreate, GroupUpdate, MembershipCreate


class GroupRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_group(self, group: GroupCreate):
        max_group_id = self.db.query(func.max(Group.id)).scalar() or 0
        new_group_id = max_group_id + 1

        db_group = Group(id=new_group_id, **group.dict())
        self.db.add(db_group)
        self.db.commit()
        self.db.refresh(db_group)
        return db_group

    def get_groups(self):
        return self.db.query(Group).all()

    def get_group(self, group_id: int):
        return self.db.query(Group).filter(Group.id == group_id).first()

    def get_users_in_group(self, group_id: int):
        memberships = self.db.query(Membership.id_user).filter(Membership.id_group == group_id).all()
        user_ids = [membership.id_user for membership in memberships]

        users = self.db.query(User).filter(User.id.in_(user_ids)).all()
        return users

    def get_users_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()

    def update_group(self, group_id: int, group: GroupUpdate):
        db_group = self.get_group(group_id)
        if db_group:
            for key, value in group.dict().items():
                setattr(db_group, key, value)
            self.db.commit()
            self.db.refresh(db_group)
        return db_group

    def delete_group(self, group_id: int):
        db_group = self.get_group(group_id)
        if db_group:
            self.db.delete(db_group)
            self.db.commit()
        return db_group

    def add_membership(self, membership_data: MembershipCreate):
        membership = Membership(**membership_data.dict())
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def remove_user_from_group(self, group_id: int, user_id: int):
        membership = self.db.query(Membership).filter(Membership.id_user == user_id,
                                                      Membership.id_group == group_id).first()
        if membership:
            self.db.delete(membership)
            self.db.commit()
        return self.get_group(group_id)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_id(self, user_id: int):
        return self.db.query(User).filter(User.id == user_id).first()
