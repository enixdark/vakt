import json

from sqlalchemy import Column, Integer, SmallInteger, String, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from ...policy import Policy, ALLOW_ACCESS, DENY_ACCESS

Base = declarative_base()


class PolicySubjectModel(Base):
    """Storage model for policy subjects"""

    __tablename__ = 'vakt_policy_subjects'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    subject = Column(Text())


class PolicyResourceModel(Base):
    """Storage model for policy resources"""

    __tablename__ = 'vakt_policy_resources'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    resource = Column(Text())


class PolicyActionModel(Base):
    """Storage model for policy actions"""

    __tablename__ = 'vakt_policy_actions'

    id = Column(Integer, primary_key=True)
    uid = Column(String(255), ForeignKey('vakt_policies.uid', ondelete='CASCADE'))
    action = Column(Text())


class PolicyModel(Base):
    """Storage model for policy"""

    __tablename__ = 'vakt_policies'

    uid = Column(String(255), primary_key=True)
    type = Column(SmallInteger)
    description = Column(Text())
    effect = Column(Boolean())
    context = Column(Text())
    subjects = relationship(PolicySubjectModel, passive_deletes=True, lazy='joined')
    resources = relationship(PolicyResourceModel, passive_deletes=True, lazy='joined')
    actions = relationship(PolicyActionModel, passive_deletes=True, lazy='joined')

    @classmethod
    def from_policy(cls, policy):
        """
            Instantiate from policy object

            :param policy: object of type policy
        """
        rvalue = cls()
        return cls._create(policy, model=rvalue)

    def update(self, policy):
        """
            Update object attributes to match given policy

            :param policy: object of type policy
        """
        self._create(policy, model=self)

    def to_policy(self):
        """
            Create a policy object

            :return: object of type `Policy`
        """
        policy_dict = {
            "uid": self.uid,
            "effect": ALLOW_ACCESS if self.effect else DENY_ACCESS,
            "description": self.description,
            "context": json.loads(self.context),
            "subjects": [json.loads(x.subject) for x in self.subjects],
            "resources": [json.loads(x.resource) for x in self.resources],
            "actions": [json.loads(x.action) for x in self.actions]
        }
        policy_json = json.dumps(policy_dict)
        return Policy.from_json(policy_json)

    @classmethod
    def _create(cls, policy, model):
        """
            Helper to create PolicyModel from Policy object for add and update operations.

            :param policy: object of type Policy
            :param model: object of type PolicyModel
        """
        policy_json = policy.to_json()
        policy_dict = json.loads(policy_json)
        model.uid = policy_dict['uid']
        model.type = policy_dict['type']
        model.effect = policy_dict['effect'] == ALLOW_ACCESS
        model.description = policy_dict['description']
        model.context = json.dumps(policy_dict['context'])
        model.subjects = [PolicySubjectModel(subject=json.dumps(subject)) for subject in policy_dict['subjects']]
        model.resources = [PolicyResourceModel(resource=json.dumps(resource)) for resource in policy_dict['resources']]
        model.actions = [PolicyActionModel(action=json.dumps(action)) for action in policy_dict['actions']]
        return model
