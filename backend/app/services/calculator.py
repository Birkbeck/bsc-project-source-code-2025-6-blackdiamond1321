"""Investment calculator compound-interest projection """

from app.schemas import CalculatorRequest, CalculatorResponse, CalculatorMonth


class CalculatorService:
    """Compound-interest projection with regular monthly investments."""

    def project(self, data: CalculatorRequest) -> CalculatorResponse:
        """Month by month projection. Add interest, then monthly investments"""
        monthly_rate = (data.annual_rate_pct / 100) / 12
        balance = data.principal
        contributed = 0.0
        months: list[CalculatorMonth] = []

        for m in range(1, data.years * 12 + 1):
            balance += balance * monthly_rate # grow first
            balance += data.monthly_contribution # then add the new money
            contributed += data.monthly_contribution

            months.append(CalculatorMonth(
                month = m,
                balance = round(balance, 2),
                contributions = round(data.principal + contributed, 2),
                interest = round(balance - data.principal - contributed, 2),
            ))

        return CalculatorResponse(
            months = months,
            total_balance = round(balance, 2),
            total_invested = round(data.principal + contributed, 2),
            total_interest = round(balance - data.principal - contributed, 2),
        )