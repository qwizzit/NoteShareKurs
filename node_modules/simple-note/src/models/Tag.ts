import type { InterfaceTagDto } from "@src/models/InterfaceTagDto.ts";

export class Tag implements InterfaceTagDto {
  readonly id: number;

  readonly name: string;

  constructor(id: number, name: string) {
    this.id = id;
    this.name = name;
  }
}