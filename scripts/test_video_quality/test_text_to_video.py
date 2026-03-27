import asyncio
import httpx
import argparse
import os

async def generate_pipeline(prompt: str, base_url: str, token: str, output_dir: str):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"[*] Testing Text-to-Video Pipeline")
    print(f"[*] Prompt: {prompt}")
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        # Step 1: Generate Image from Text
        print("\n[1/2] Generating Image from text prompt...")
        try:
            img_resp = await client.post(
                f"{base_url}/api/v1/generate/image",
                json={"prompt": prompt},
                headers=headers
            )
            
            if img_resp.status_code != 200:
                print(f"[-] Failed to generate image. Status: {img_resp.status_code}")
                print(img_resp.text)
                return
                
            image_path = os.path.join(output_dir, "generated_image.png")
            with open(image_path, "wb") as f:
                f.write(img_resp.content)
            
            print(f"[+] Image successfully generated and saved to {image_path}")
            
        except Exception as e:
            print(f"[-] Exception during image generation: {e}")
            return
            
        # Step 2: Generate Video from Image
        print("\n[2/2] Generating Video from the generated image...")
        try:
            video_payload = {
                "caption": "Your daily astral forecast reveals new beginnings and hidden opportunities."
            }
            with open(image_path, "rb") as f:
                files = {"file": ("generated_image.png", f, "image/png")}
                vid_resp = await client.post(
                    f"{base_url}/api/v1/generate/video",
                    data=video_payload,
                    files=files,
                    headers=headers
                )
                
            if vid_resp.status_code != 200:
                print(f"[-] Failed to generate video. Status: {vid_resp.status_code}")
                print(vid_resp.text)
                return
                
            video_path = os.path.join(output_dir, "generated_video.mp4")
            with open(video_path, "wb") as f:
                f.write(vid_resp.content)
                
            print(f"[+] Video successfully generated and saved to {video_path}")
            print(f"\n[*] Pipeline Test Complete. Check the '{output_dir}' directory for results.")
            
        except Exception as e:
            print(f"[-] Exception during video generation: {e}")
            return

def main():
    parser = argparse.ArgumentParser(description="Test Text-to-Video Generation Quality")
    parser.add_argument("--prompt", type=str, required=True, help="Text prompt to generate the video from")
    parser.add_argument("--base-url", type=str, default="http://localhost:8000", help="Base URL of the API server")
    parser.add_argument("--token", type=str, default="", help="Auth token if required by the backend")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory to save the generated files")
    
    args = parser.parse_args()
    
    asyncio.run(generate_pipeline(args.prompt, args.base_url, args.token, args.output_dir))

if __name__ == "__main__":
    main()
