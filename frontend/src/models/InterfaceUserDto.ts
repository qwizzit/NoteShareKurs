import type { InterfaceSettingsDto } from "@src/models/InterfaceSettingsDto.ts";

export interface InterfaceUserDto {
  email: string;

  // password: string;

  theme: string;

  readonly id: number;

  settings: InterfaceSettingsDto
}

export interface InterfaceShortUserDto {
  readonly id: number;

  readonly email: string;
}