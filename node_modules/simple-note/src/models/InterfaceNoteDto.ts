import type { InterfaceTagDto } from "@src/models/InterfaceTagDto.ts";

export interface InterfaceNoteDto {
  readonly id: number;

  readonly created_at: string;

  readonly userId: number;

  title: string;

  content: string;

  tags: { id: number, name: string }[];

  color: string;

  updated_at: string;

  get summary(): string;
}

export interface InterfaceNoteShortDto extends InterfaceTagDto {
  readonly id: number;

  readonly created_at: string;

  readonly userId: number;

  title: string;

  tags: InterfaceTagDto[];

  color: string;

  updated_at: string;

  get summary(): string;
}