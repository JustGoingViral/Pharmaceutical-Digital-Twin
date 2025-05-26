import unittest
from unittest.mock import patch
from nlg_regulator import NLGRegulatoryGenerator

class TestNLGRegulatoryGenerator(unittest.TestCase):

    @patch('openai.ChatCompletion.create')
    def test_generate_fda_report(self, mock_create):
        mock_create.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is a mocked FDA report for testing purposes.'
                }
            }]
        }

        generator = NLGRegulatoryGenerator(api_key="test-api-key")
        anomalies = {
            "impurity_level": "Exceeded threshold in sample 17A",
            "temperature_variation": "Spike of +2°C during synthesis",
        }
        report = generator.generate_fda_report("TestDrug", "BATCH999", anomalies)
        self.assertIn("mocked FDA report", report)

if __name__ == "__main__":
    unittest.main()
