
import unittest

from pydantic import ValidationError

from nexo_llm.schemas import (
    ChatMessage,
    ModelConfig,
    ModelResponse,
)


class TestChatMessage(unittest.TestCase):

    def test_valid_roles(self):
        for role in ("system", "user", "assistant"):
            with self.subTest(role=role):
                message = ChatMessage(
                    role=role,
                    content="Mensaje de prueba"
                )

                self.assertEqual(message.role, role)

    def test_invalid_role(self):
        with self.assertRaises(ValidationError):
            ChatMessage(
                role="admin",
                content="Mensaje de prueba"
            )

    def test_empty_content(self):
        with self.assertRaises(ValidationError):
            ChatMessage(
                role="user",
                content=""
            )

    def test_missing_content(self):
        with self.assertRaises(ValidationError):
            ChatMessage(
                role="user"
            )


class TestModelConfig(unittest.TestCase):

    def test_valid_config(self):
        config = ModelConfig(
            model="modelo-de-prueba",
            temperature=0.7,
            max_tokens=500
        )

        self.assertEqual(config.model, "modelo-de-prueba")
        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 500)

    def test_default_values(self):
        config = ModelConfig(
            model="modelo-de-prueba"
        )

        self.assertEqual(config.temperature, 0.7)
        self.assertEqual(config.max_tokens, 500)

    def test_temperature_boundaries(self):
        for temperature in (0, 2):
            with self.subTest(temperature=temperature):
                config = ModelConfig(
                    model="modelo-de-prueba",
                    temperature=temperature
                )

                self.assertEqual(
                    config.temperature,
                    temperature
                )

    def test_temperature_below_minimum(self):
        with self.assertRaises(ValidationError):
            ModelConfig(
                model="modelo-de-prueba",
                temperature=-0.1
            )

    def test_temperature_above_maximum(self):
        with self.assertRaises(ValidationError):
            ModelConfig(
                model="modelo-de-prueba",
                temperature=2.1
            )

    def test_zero_max_tokens(self):
        with self.assertRaises(ValidationError):
            ModelConfig(
                model="modelo-de-prueba",
                max_tokens=0
            )

    def test_negative_max_tokens(self):
        with self.assertRaises(ValidationError):
            ModelConfig(
                model="modelo-de-prueba",
                max_tokens=-10
            )

    def test_empty_model(self):
        with self.assertRaises(ValidationError):
            ModelConfig(
                model=""
            )


class TestModelResponse(unittest.TestCase):

    def test_valid_response(self):
        response = ModelResponse(
            provider="openai",
            model="modelo-de-prueba",
            content="La entropía mide la incertidumbre."
        )

        self.assertEqual(response.provider, "openai")
        self.assertEqual(response.model, "modelo-de-prueba")
        self.assertEqual(
            response.content,
            "La entropía mide la incertidumbre."
        )

    def test_missing_provider(self):
        with self.assertRaises(ValidationError):
            ModelResponse(
                model="modelo-de-prueba",
                content="Respuesta de prueba"
            )

    def test_missing_content(self):
        with self.assertRaises(ValidationError):
            ModelResponse(
                provider="openai",
                model="modelo-de-prueba"
            )


if __name__ == "__main__":
    unittest.main()
