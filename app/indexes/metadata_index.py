class MetadataIndex:
    @staticmethod
    def match(metadata: dict, filters: dict) -> bool:
        return all(value in {None, "", "all"} or metadata.get(key) == value for key, value in filters.items())
