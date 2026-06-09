export interface InterfaceTagDto {
  id: number;

  name: string;
}

export interface InterfaceUserTags {
  id: number;

  name: string;

  /**
   * @deprecated
   */
  note_ids: Set<number>;
}