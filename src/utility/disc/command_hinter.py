from abc import ABC, abstractmethod
from difflib import SequenceMatcher
from typing import List, Union, Optional, Any
import inspect
import discord
from discord.ext import commands


class InvalidGenerator(Exception):
    """
    Raises an exception when the user passes an invalid generator.
    """

    __slots__ = ("generator",)

    def __init__(self, generator):
        self.generator = generator
        super().__init__(
            f"Generator of type {type(self.generator)!r} is not supported."
        )


def get_generator_response(generator: Any, generator_type: Any, *args, **kwargs) -> Any:
    """
    Returns the generator response with the arguments.
    :param generator: The generator to get the response from.
    :type generator: Any
    :param generator_type: The generator type. (Should be same as the generator type.
    :type generator_type: Any
    :param args: The arguments of the generator.
    :param kwargs: The key arguments of the generator
    :return: The generator response.
    :rtype: Any
    """

    if inspect.isclass(generator) and issubclass(generator, generator_type):
        if inspect.ismethod(generator.generate):
            return generator.generate(*args, **kwargs)

        return generator().generate(*args, **kwargs)

    if isinstance(generator, generator_type):
        return generator.generate(*args, **kwargs)

    raise InvalidGenerator(generator)


__all__ = ("CommandResponseGenerator", "DefaultResponseGenerator", "CommandHinter")


class CommandResponseGenerator(ABC):
    """
    Represents the default abstract CommandResponseGenerator.
    """

    __slots__ = ()

    @abstractmethod
    def generate(
        self, invalid_command: str, suggestions: List[str]
    ) -> Optional[Union[str, discord.Embed]]:
        """
        The generate method of the generator.
        :param str invalid_command: The invalid command.
        :param List[str] suggestions: The list of suggestions.
        :return: The generator response.
        :rtype: Optional[Union[str, discord.Embed]]
        """


class DefaultResponseGenerator(CommandResponseGenerator):
    __slots__ = ()

    def generate(self, invalid_command: str, suggestions: List[str]) -> discord.Embed:
        """
        The default generate method of the generator.
        :param str invalid_command: The invalid command.
        :param List[str] suggestions: The list of suggestions.
        :return: The generator response.
        :rtype: discord.Embed
        """

        embed = discord.Embed(
            title="Invalid command!",
            description=f"**`{invalid_command}`** is invalid. Did you mean:",
            color=0x00FF00,
        )

        for index, suggestion in enumerate(suggestions[:3]):
            embed.add_field(
                name=f"**{index + 1}.**", value=f"**`{suggestion}`**", inline=False
            )

        return embed


class CommandHinter:
    """
    Represents a command hinter.
    """

    __slots__ = ("bot", "generator")

    def __init__(
        self, bot: commands.Bot, generator: Optional[CommandResponseGenerator] = None
    ):
        """
        :param commands.Bot bot: The bot.
        :param Optional[CommandResponseGenerator] generator: The command response generator.
        """

        self.bot = bot
        self.generator = DefaultResponseGenerator if generator is None else generator

        self.bot.add_listener(self.__handle_hinter, "on_command_error")

    @property
    def command_names(self) -> List[str]:
        """
        Returns the command names of all commands of the bot.
        :return: The command names.
        :rtype: List[str]
        """

        names = []

        for command in self.bot.commands:
            if isinstance(command, commands.Group):
                names += [command.name] + list(command.aliases)

            else:
                names += [command.name] + list(command.aliases)

        return names

    async def __handle_hinter(self, ctx: commands.Context, error) -> None:
        if isinstance(error, commands.CommandNotFound):
            command_similarity = {}
            command_used = ctx.message.content.lstrip(ctx.prefix)[
                : max([len(c) for c in self.command_names])
            ]

            for command in self.command_names:
                command_similarity[
                    SequenceMatcher(None, command, command_used).ratio()
                ] = command

            # Filter it so that the match ratio is at least 0.5
            command_similarity = {
                k: v for k, v in command_similarity.items() if k >= 0.7
            }

            generated_message = get_generator_response(
                self.generator,
                CommandResponseGenerator,
                command_used,
                [x[1] for x in sorted(command_similarity.items(), reverse=True)],
            )

            if not generated_message:
                return

            if isinstance(generated_message, discord.Embed):
                await ctx.send(embed=generated_message)
            elif isinstance(generated_message, str):
                await ctx.send(generated_message)
            else:
                raise TypeError(
                    "The generated message must be of type 'discord.Embed' or 'str'."
                )


class CommandGenerator(CommandResponseGenerator):
    def generate(
        self, invalid_command: str, suggestions: List[str]
    ) -> Optional[Union[str, discord.Embed]]:
        if suggestions:
            return discord.Embed(
                title=f"`{invalid_command}` not found.",
                description=f"Did you mean `{suggestions[0]}`?",
                colour=0x2F3136,
            )
