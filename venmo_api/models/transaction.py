from decimal import Decimal
from enum import Enum

from venmo_api import (
    string_to_timestamp,
    BaseModel,
    User,
    Comment,
    get_phone_model_from_json,
)


class Transaction(BaseModel):
    def __init__(
        self,
        story_id,
        payment_id,
        date_completed,
        date_created,
        date_updated,
        payment_type,
        amount,
        audience,
        status,
        note,
        device_used,
        actor,
        target,
        comments,
        json=None,
    ):
        """
        Transaction model
        """
        super().__init__()

        self.id = story_id
        self.payment_id = payment_id

        self.date_completed = date_completed
        self.date_created = date_created
        self.date_updated = date_updated

        self.payment_type = payment_type
        self.amount = amount
        self.audience = audience
        self.status = status

        self.note = note
        self.device_used = device_used
        self.comments = comments

        self.actor = actor
        self.target = target
        self._json = json

    @classmethod
    def from_json(cls, json):
        """
        Create a new Transaction from the given json.
        This only works for transactions, skipping refunds and bank transfers.
        """

        if not json:
            return

        payment_json = json.get("payment")
        transaction_type = TransactionType(json.get("type"))

        # Currently only handles Payment-type transactions
        if transaction_type is not TransactionType.PAYMENT:
            return

        date_created = string_to_timestamp(json.get("date_created"))
        date_updated = string_to_timestamp(json.get("date_updated"))
        date_completed = string_to_timestamp(json.get("date_completed"))
        target = User.from_json(payment_json.get("target").get("user"))
        actor = User.from_json(payment_json.get("actor"))
        device_used = get_phone_model_from_json(json.get("app"))

        comments = json.get("comments", {}).get("comments_list")
        comments = [Comment.from_json(json=comment) for comment in comments] if comments else []

        return cls(
            story_id=json.get("id"),
            payment_id=payment_json.get("id"),
            payment_type=payment_json.get("action"),
            amount=int(Decimal(payment_json.get("amount")) * 100),
            audience=json.get("audience"),
            note=payment_json.get("note"),
            status=payment_json.get("status"),
            date_completed=date_completed,
            date_created=date_created,
            date_updated=date_updated,
            device_used=device_used,
            actor=actor,
            target=target,
            comments=comments,
            json=json,
        )


class TransactionType(Enum):
    PAYMENT = "payment"
    # merchant refund
    REFUND = "refund"
    # to/from bank account
    TRANSFER = "transfer"
    # add money to debit card
    TOP_UP = "top_up"
    # debit card purchase
    AUTHORIZATION = "authorization"
    # debit card atm withdrawal
    ATM_WITHDRAWAL = "atm_withdrawal"
    # ???
    DISBURSEMENT = "disbursement"
