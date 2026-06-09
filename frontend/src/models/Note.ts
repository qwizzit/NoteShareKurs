import { Tag } from "@src/models/Tag.ts";
import type { InterfaceNoteDto } from "src/models/InterfaceNoteDto.ts";

export class Note implements InterfaceNoteDto {
  readonly id: number;

  readonly userId: number;

  constructor(
    id: number,
    userId: number,
    title: string,
    color: string = '#B2BEB5',
    createdAt: string,
    updatedAt: string,
    content: string = '',
  ) {
    this.id = id;
    this.userId = userId;
    this._title = title;
    this._color = color;
    this._created_at = createdAt;
    this._updated_at = updatedAt
    this._content = content;
  }

  private _created_at: string;

  get created_at(): string {
    return new Date(this._created_at).toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/\//g, '.');
  }

  private _updated_at: string;

  get updated_at(): string {
    return new Date(this._updated_at).toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/\//g, '.');
  }

  set updated_at(updated_at: string) {
    this._updated_at = updated_at;
  }

  private _summary: string = '';

  get summary() {
    return this._content.length > 0
      ? this._content.slice(0, 100)
      : this._summary;
  }

  private _title: string;

  get title(): string {
    return this._title;
  }

  set title(value: string) {
    this._title = value.length > 0 ? value : "";
  }

  private _content: string = '';

  get content(): string {
    return this._content;
  }

  set content(value: string) {
    this._content = value;
  }

  private _tags: Tag[] = [];

  get tags(): Tag[] {
    return this._tags;
  }

  set tags(value: { id: number, name: string }[]) {
    this._tags = value;
  }

  private _color: string;

  get color() {
    return this._color;
  }

  set color(value: string) {
    this._color = value;
  }

  // eslint-disable-next-line @typescript-eslint/member-ordering
  addTag(newTag: { id: number, name: string }) {
    this._tags = [ ...this._tags, new Tag(newTag.id, newTag.name) ];
  }

  // eslint-disable-next-line @typescript-eslint/member-ordering
  removeTag(id: number) {
    const index = this._tags.findIndex(tag => tag.id === id);
    if (index !== -1) {
      this._tags.splice(index, 1);
    }
  }
}