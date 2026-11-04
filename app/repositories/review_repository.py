"""
도자기 원데이 클래스 리뷰 저장소.

데이터베이스 대신 딕셔너리를 사용하여 리뷰를 메모리에 저장한다.
서버를 종료하면 저장된 리뷰는 사라진다.
"""

from app.domain.review import Review


class ReviewRepository:
    """리뷰를 저장하고 조회하는 딕셔너리 기반 저장소."""

    def __init__(self):
        # 리뷰 번호를 키로, Review 객체를 값으로 저장한다.
        self._reviews: dict[int, Review] = {}

        # 다음 신규 리뷰에 부여할 번호다.
        # 첫 번째 리뷰는 1번부터 시작한다.
        self._next_id = 1

    def save(self, review: Review) -> Review:
        """
        리뷰를 저장한다.

        review_id가 0인 신규 리뷰에는 새로운 번호를 부여한다.
        이미 번호가 있는 리뷰는 같은 번호의 데이터를 덮어쓴다.

        Args:
            review (Review): 저장할 리뷰

        Returns:
            Review: 번호가 부여되어 저장된 리뷰
        """

        # 신규 리뷰라면 다음 리뷰 번호를 부여한다.
        if review.review_id == 0:
            review.review_id = self._next_id
            self._next_id += 1

        # 리뷰 번호를 키로 사용하여 Review 객체를 저장한다.
        self._reviews[review.review_id] = review

        return review

    def find_by_id(self, review_id: int) -> Review | None:
        """
        리뷰 번호로 리뷰 하나를 조회한다.

        Args:
            review_id (int): 조회할 리뷰 번호

        Returns:
            Review | None: 조회한 리뷰. 존재하지 않으면 None
        """

        # 대괄호를 사용하면 없는 키에서 KeyError가 발생하므로
        # get()을 사용하여 존재하지 않을 때 None을 반환한다.
        return self._reviews.get(review_id)
