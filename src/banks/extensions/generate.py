# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from typing import cast

from jinja2 import nodes
from jinja2.ext import Extension
from litellm import ModelResponse, completion, acompletion

DEFAULT_MODEL = "gpt-3.5-turbo"


class GenerateExtension(Extension):
    """
    `generate` can be used to call the LiteLLM API passing the tag text as a prompt and get back some content.

    Example:
        ```
        {% generate "write a tweet with positive sentiment" "gpt-3.5-turbo" %}
        Feeling grateful for all the opportunities that come my way! #positivity #productivity
        ```
    """

    # a set of names that trigger the extension.
    tags = {"generate"}  # noqa

    def parse(self, parser):
        # We get the line number of the first token so that we can give
        # that line number to the nodes we create by hand.
        lineno = next(parser.stream).lineno

        # The args passed to the extension:
        # - the prompt text used to generate new text
        # - (optional) the name of the model use to generate new text
        args = [parser.parse_expression()]

        # If there is a comma, the user provided the model name. If not, use
        # None as the second parameter.
        if parser.stream.skip_if("comma"):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const(None))

        if parser.environment.is_async:
            return nodes.Output([self.call_method("_agenerate", args)]).set_lineno(lineno)
        return nodes.Output([self.call_method("_generate", args)]).set_lineno(lineno)

    def _generate(self, text, model_name=DEFAULT_MODEL):
        """
        Helper callback.

        To tweak the prompt used to generate content, change the variable `messages` .
        """
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text},
        ]
        response: ModelResponse = cast(ModelResponse, completion(model=model_name, messages=messages))
        return response["choices"][0]["message"]["content"]

    async def _agenerate(self, text, model_name=DEFAULT_MODEL):
        """
        Helper callback.

        To tweak the prompt used to generate content, change the variable `messages` .
        """
        print(f"Running {text} with {model_name}")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": text},
        ]
        response: ModelResponse = cast(ModelResponse, await acompletion(model=model_name, messages=messages))
        print(f"Done running {model_name}")
        return response["choices"][0]["message"]["content"]
