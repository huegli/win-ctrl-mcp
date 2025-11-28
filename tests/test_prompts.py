"""Tests for MCP prompts."""

from win_ctrl_mcp.prompts import PROMPTS


class TestPromptDefinitions:
    """Tests for prompt definitions."""

    def test_organize_windows_prompt_exists(self):
        """Test that organize_windows prompt is defined."""
        assert "organize_windows" in PROMPTS
        prompt = PROMPTS["organize_windows"]
        assert "description" in prompt
        assert "template" in prompt
        assert "arguments" in prompt

    def test_smart_focus_prompt_exists(self):
        """Test that smart_focus prompt is defined."""
        assert "smart_focus" in PROMPTS
        prompt = PROMPTS["smart_focus"]
        assert "description" in prompt
        assert "template" in prompt
        assert "arguments" in prompt
        # Smart focus should have multiple arguments
        assert len(prompt["arguments"]) >= 3

    def test_presentation_layout_prompt_exists(self):
        """Test that presentation_layout prompt is defined."""
        assert "presentation_layout" in PROMPTS
        prompt = PROMPTS["presentation_layout"]
        assert "description" in prompt
        assert "template" in prompt
        assert "arguments" in prompt

    def test_debug_app_gui_prompt_exists(self):
        """Test that debug_app_gui prompt is defined."""
        assert "debug_app_gui" in PROMPTS
        prompt = PROMPTS["debug_app_gui"]
        assert "description" in prompt
        assert "template" in prompt
        assert "arguments" in prompt

    def test_all_prompts_have_required_fields(self):
        """Test that all prompts have required fields."""
        required_fields = ["description", "template", "arguments"]

        for name, prompt in PROMPTS.items():
            for field in required_fields:
                assert field in prompt, f"Prompt '{name}' missing field '{field}'"

    def test_prompt_arguments_have_required_fields(self):
        """Test that prompt arguments have required fields."""
        for name, prompt in PROMPTS.items():
            for arg in prompt["arguments"]:
                assert "name" in arg, f"Argument in '{name}' missing 'name'"
                assert "description" in arg, f"Argument in '{name}' missing 'description'"
                assert "required" in arg, f"Argument in '{name}' missing 'required'"

    def test_organize_windows_template_content(self):
        """Test organize_windows template has expected content."""
        template = PROMPTS["organize_windows"]["template"]
        assert "window management tools" in template.lower()
        assert "aerospace://windows" in template

    def test_smart_focus_template_content(self):
        """Test smart_focus template has expected content."""
        template = PROMPTS["smart_focus"]["template"]
        assert "display" in template.lower()
        assert "focus" in template.lower()

    def test_presentation_layout_template_content(self):
        """Test presentation_layout template has expected content."""
        template = PROMPTS["presentation_layout"]["template"]
        assert "presentation" in template.lower()
        assert "fullscreen" in template.lower()

    def test_debug_app_gui_template_content(self):
        """Test debug_app_gui template has expected content."""
        template = PROMPTS["debug_app_gui"]["template"]
        assert "capture" in template.lower()
        assert "debug" in template.lower()
