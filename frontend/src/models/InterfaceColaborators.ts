import type { InterfaceShortUserDto } from "@src/models/InterfaceUserDto.ts";

export interface InterfaceColaborators {
  owner: InterfaceShortUserDto,

  collaborators: InterfaceShortUserDto[],
}