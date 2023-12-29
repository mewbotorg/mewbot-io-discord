def split_text(target_txt: str, char_limit: int = 2000) -> list[str]:
    """
    Split the text down into discord compliant chunks.

    :param target_txt: The text to split down
    :param char_limit: Maximum number of chars in a chunk
    :return:
    """

    # if len(target_txt) < char_limit:
    #     return [target_txt, ]
    #

    cand_txt_tokens = target_txt.split("\n")

    intermediate_tokens = []
    for cand_token in cand_txt_tokens:
        # If we have a token of less than char_limit - all good - just include it
        if len(cand_token) < char_limit:
            intermediate_tokens.append(cand_token)
            continue

        # If we have a longer token, more surgery is needed
        split_cand_tokens = [
            cand_token[i : i + char_limit] for i in range(0, len(cand_token), char_limit)
        ]
        intermediate_tokens.extend(split_cand_tokens)

    # Regroup the tokens to minimise messages
    # The aim is chunks less than char_limit characters
    acc_tokens_list: list[str] = []
    running_count: int = 0
    final_tokens: list[str] = []
    for token in intermediate_tokens:
        # reset - we can accumulate no more
        if running_count + len(token) > char_limit:
            final_tokens.append("\n".join(acc_tokens_list))
            running_count = len(token)
            acc_tokens_list = [
                token,
            ]
            continue

        # Accumulate
        acc_tokens_list.append(token)
        running_count += len(token)

    # Finalise
    final_tokens.append("\n".join(acc_tokens_list))

    return final_tokens
